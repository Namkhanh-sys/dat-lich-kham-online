import json
import re
import threading
from collections import OrderedDict
from google import genai
from google.genai import types
from config import Config
from src.symptom_matcher import SymptomMatcher
from src.distance_calculator import DistanceCalculator
from src.csv_helper import CSVHelper

# Prompt hệ thống — rút gọn tối đa để tiết kiệm token
SYSTEM_PROMPT = """Bạn là trợ lý y tế AI đặt lịch khám Việt Nam. Trả lời tiếng Việt, ngắn gọn (≤4 câu/tin).

QUY TRÌNH (bắt buộc):
1. Nhận triệu chứng → hỏi 1 câu làm rõ + OPTIONS.["...","..."]
2. Hỏi thêm ít nhất 2 lần (mỗi lần chỉ 1 câu + OPTIONS).
3. Sau ≥2 lượt hỏi–đáp → đưa kết luận + DOCTOR_SUGGESTION (không kèm OPTIONS).

FORMAT:
Câu hỏi của bạn.
OPTIONS:["lựa chọn 1","lựa chọn 2","lựa chọn 3"]

QUY TẮC KHÁC:
- Mỗi tin nhắn tối đa 4 câu, ngắn gọn, không dài dòng
- Không dùng OPTIONS lẫn DOCTOR_SUGGESTION trong cùng một tin nhắn
- Không chẩn đoán bệnh cụ thể, chỉ gợi ý chuyên khoa
- Dùng tiếng Việt đơn giản, thân thiện, ân cần
- Hệ thống sẽ tự hiển thị danh sách bác sĩ, chatbot KHÔNG cần liệt kê"""

GREETING = "Xin chào! Tôi là trợ lý y tế AI 🏥\n\nTôi có thể giúp bạn nhận định sơ bộ về các triệu chứng và gợi ý chuyên khoa phù hợp để đặt lịch khám.\n\nBạn đang gặp phải vấn đề sức khỏe gì? Hãy mô tả triệu chứng của bạn nhé! 😊"


class GeminiChatbot:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton — chỉ tạo 1 instance duy nhất với Thread-safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        try:
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
            self.model_name = 'gemini-2.5-flash'  # Succeeded in testing
        except Exception as e:
            print(f"[CHATBOT] Gemini init error: {e}")
            self.client = None
            self.model_name = None
        # chat_sessions: OrderedDict làm LRU cache tự chế tránh tràn RAM
        self.chat_sessions = OrderedDict()
        self.max_sessions = 1000
        self.max_history_len = 10  # Giữ 10 tin nhắn gần nhất để tiết kiệm token
        self._available = self.client is not None
        self._initialized = True

    @property
    def is_available(self):
        groq_key = getattr(Config, 'GROQ_API_KEY', '')
        gemini_key = getattr(Config, 'GEMINI_API_KEY', '')
        has_groq = bool(groq_key) and groq_key.strip() not in ('', 'PASTE_YOUR_KEY_HERE')
        has_gemini = self._available and bool(gemini_key) and gemini_key.strip() not in ('', 'PASTE_YOUR_KEY_HERE')
        return has_groq or has_gemini

    def _get_history(self, session_id: str) -> list:
        """Lấy lịch sử chat (list of dict). Khởi tạo với greeting nếu chưa có."""
        if session_id in self.chat_sessions:
            # Di chuyển lên cuối cùng để đánh dấu là mới dùng (LRU Cache)
            if hasattr(self.chat_sessions, 'move_to_end'):
                self.chat_sessions.move_to_end(session_id)
        else:
            # Nếu vượt quá số lượng session tối đa, xóa session cũ nhất
            if len(self.chat_sessions) >= self.max_sessions:
                if hasattr(self.chat_sessions, 'popitem'):
                    try:
                        self.chat_sessions.popitem(last=False)
                    except TypeError:
                        self.chat_sessions.popitem()
                elif self.chat_sessions:
                    self.chat_sessions.pop(next(iter(self.chat_sessions)))
            # Khởi tạo lịch sử chat dạng dict lists
            self.chat_sessions[session_id] = [
                {
                    "role": "assistant",
                    "content": GREETING
                }
            ]
        return self.chat_sessions[session_id]

    def chat(self, session_id: str, user_message: str, lat=None, lon=None, province=None, district=None, location_source=None) -> dict:
        """
        Gửi tin nhắn, nhận phản hồi từ Groq (hoặc Gemini dự phòng), trích xuất gợi ý bác sĩ và options.
        Trả về: {"reply": str, "doctors": list, "advice": str, "options": list}
        """
        if not self.is_available:
            return {
                "reply": "⚠️ Chatbot AI chưa được cấu hình. Vui lòng kiểm tra API Key trong config.py.",
                "doctors": [],
                "advice": "",
                "options": []
            }



        try:
            # Đảm bảo luồng an toàn khi truy xuất và cập nhật lịch sử
            with self._lock:
                history = self._get_history(session_id)

                # Thêm tin nhắn người dùng vào lịch sử
                history.append({
                    "role": "user",
                    "content": user_message
                })

                # Giới hạn lịch sử chat (Sliding Window) để tiết kiệm token đầu vào
                if len(history) > self.max_history_len:
                    history = [history[0]] + history[-(self.max_history_len - 1):]
                    self.chat_sessions[session_id] = history

            # Di chuyển cấu hình động hoặc tính toán số câu hỏi đã hỏi
            active_prompt = SYSTEM_PROMPT
            user_msg_count = sum(1 for m in history if m["role"] == "user")
            if user_msg_count >= 3:
                active_prompt += "\n\n⚠️ YÊU CẦU BẮT BUỘC: Bạn đã thu thập đủ thông tin (qua 3 tin nhắn của người dùng). KHÔNG ĐƯỢC HỎI THÊM NỮA. Hãy đưa ra kết luận phân tích triệu chứng chi tiết và gợi ý chuyên khoa phù hợp dưới dạng DOCTOR_SUGGESTION ngay trong tin nhắn này. Tuyệt đối KHÔNG xuất hiện OPTIONS."

            full_reply = None

            # 1. PRIMARY: Gemini 1.5-flash (1500 RPD, ổn định)
            if self._available and self.client:
                try:
                    gemini_key = getattr(Config, 'GEMINI_API_KEY', '')
                    if bool(gemini_key) and gemini_key.strip() not in ('', 'PASTE_YOUR_KEY_HERE'):
                        gemini_history = []
                        for h in history:
                            role = "model" if h["role"] == "assistant" else h["role"]
                            gemini_history.append(
                                types.Content(role=role, parts=[types.Part(text=h["content"])])
                            )
                        resp = self.client.models.generate_content(
                            model=self.model_name,
                            contents=gemini_history,
                            config=types.GenerateContentConfig(
                                system_instruction=active_prompt,
                                temperature=0.85,
                                max_output_tokens=400,
                            )
                        )
                        full_reply = resp.text
                except Exception as gem_err:
                    print(f"[CHATBOT] Gemini failed: {gem_err}. Falling back to Groq...")

            # 2. FALLBACK: Groq (nhanh nhưng TPM giới hạn)
            if full_reply is None:
                groq_key = getattr(Config, 'GROQ_API_KEY', '')
                if bool(groq_key) and groq_key.strip() not in ('', 'PASTE_YOUR_KEY_HERE'):
                    try:
                        import requests
                        headers = {
                            "Authorization": f"Bearer {groq_key.strip()}",
                            "Content-Type": "application/json"
                        }
                        messages = [{"role": "system", "content": active_prompt}] + history
                        payload = {
                            "model": "llama-3.3-70b-versatile",
                            "messages": messages,
                            "temperature": 0.85,
                            "max_tokens": 400
                        }
                        response = requests.post(
                            "https://api.groq.com/openai/v1/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=8
                        )
                        if response.status_code == 200:
                            full_reply = response.json()["choices"][0]["message"]["content"]
                            print("[CHATBOT] Used Groq fallback")
                        else:
                            print(f"[CHATBOT] Groq error: {response.status_code}")
                    except Exception as groq_err:
                        print(f"[CHATBOT] Groq fallback failed: {groq_err}")

            if full_reply is None:
                raise Exception("Tất cả API đều không khả dụng. Vui lòng thử lại sau.")

            # Tách OPTIONS, DOCTOR_SUGGESTION khỏi nội dung hiển thị trước khi lưu vào lịch sử
            display_reply, options = self._extract_options(full_reply)
            display_reply, suggestion = self._extract_suggestion(display_reply)

            # Thêm phản hồi model (chỉ lưu phần hiển thị, không lưu các thẻ JSON thô) vào lịch sử
            with self._lock:
                history = self._get_history(session_id)
                history.append({
                    "role": "assistant",
                    "content": display_reply.strip()
                })

            doctors = []
            advice = ""

            if suggestion:
                keywords = suggestion.get("keywords", "")
                advice = suggestion.get("advice", "")
                specialty = suggestion.get("specialty", "")

                # Tìm bác sĩ phù hợp từ CSV
                if keywords or specialty:
                    search_text = f"{keywords} {specialty}".strip()
                    matched = SymptomMatcher.match_doctors_by_symptom(search_text)
                    
                    # Check location coordinates
                    has_coords = False
                    try:
                        if lat is not None and lon is not None:
                            user_lat = float(lat)
                            user_lon = float(lon)
                            has_coords = True
                    except (ValueError, TypeError):
                        pass

                    if has_coords:
                        # Enrich with actual distance
                        clinics_list = DistanceCalculator.get_clinics_with_distance(
                            user_lat, user_lon, province=province, district=district
                        )
                        clinics_dict = {str(c['id']).strip(): c for c in clinics_list}
                        
                        for doc in matched:
                            cid = str(doc.get('clinic_id', '')).strip()
                            clinic = clinics_dict.get(cid, {})
                            doc['clinic_name'] = clinic.get('name', 'Phòng khám chưa xác định')
                            doc['clinic_address'] = clinic.get('address', 'Chưa có địa chỉ')
                            doc['distance_km'] = clinic.get('distance_km', 9999.0)
                        
                        # Sort by distance
                        doctors = sorted(matched, key=lambda x: x.get('distance_km', 9999.0))
                    else:
                        # Fallback when coordinates are missing
                        clinics = CSVHelper.get_clinics()
                        clinics_dict = {str(c['id']).strip(): c for c in clinics.to_dict('records')}
                        
                        for doc in matched:
                            cid = str(doc.get('clinic_id', '')).strip()
                            clinic = clinics_dict.get(cid, {})
                            doc['clinic_name'] = clinic.get('name', 'Phòng khám chưa xác định')
                            doc['clinic_address'] = clinic.get('address', 'Chưa có địa chỉ')
                            doc['distance_km'] = 9999.0
                        
                        doctors = matched
                        
                        # Append warning instructing user to turn on GPS or manually select address
                        warning_note = "\n\n💡 *Gợi ý:* Bật GPS hoặc chọn vị trí tại trang chủ để tìm bác sĩ gần nhất."
                        display_reply = display_reply.strip() + warning_note

                    # Return up to 4 doctors
                    doctors = doctors[:4]

            return {
                "reply": display_reply.strip(),
                "doctors": doctors,
                "advice": advice,
                "options": options
            }

        except Exception as e:
            # Xóa tin nhắn cuối cùng (tin nhắn người dùng gửi bị lỗi) để người dùng có thể gửi lại mà không bị lặp
            with self._lock:
                history = self._get_history(session_id)
                if history and history[-1]["role"] == "user":
                    history.pop()

            import traceback
            err_traceback = traceback.format_exc()
            print(f"[CHATBOT] Error: {e}\n{err_traceback}")
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                reply_msg = "⚠️ Hạn ngạch API đã vượt quá giới hạn (Quota Exceeded). Vui lòng thử lại sau 1 phút."
            else:
                reply_msg = f"Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau."
            return {
                "reply": reply_msg,
                "doctors": [],
                "advice": "",
                "options": []
            }

    def _extract_options(self, text: str):
        """
        Tách OPTIONS:[...] ra khỏi text hiển thị.
        Trả về (display_text, options_list).
        """
        # Match OPTIONS:[...
        pattern = r'OPTIONS:\s*\[(.*)'
        match = re.search(pattern, text)
        if match:
            content = match.group(1).strip()
            # Cleanly remove the match portion from the text
            display_text = text[:match.start()].strip()
            
            # If there was text after the closing bracket of options, we keep it
            idx = content.find(']')
            after_text = ""
            if idx != -1:
                after_text = content[idx+1:].strip()
                content = content[:idx+1]
            
            # Find all quoted items inside brackets
            items = re.findall(r'["\'](.*?)["\']', content)
            if not items:
                # Fallback to comma-separated values if no quotes found
                cleaned_content = content.replace('[', '').replace(']', '').strip()
                items = [item.strip() for item in cleaned_content.split(',') if item.strip()]
            
            # Combine display text with any text that was after the options block
            if after_text:
                display_text = f"{display_text}\n{after_text}".strip()
                
            return display_text, items
            
        return text, []

    def _extract_suggestion(self, text: str):
        """
        Tách JSON DOCTOR_SUGGESTION ra khỏi text hiển thị.
        Trả về (display_text, suggestion_dict hoặc None).
        """
        pattern = r'DOCTOR_SUGGESTION:\s*(\{.*?\})'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            json_str = match.group(1)
            # Remove the DOCTOR_SUGGESTION portion from the text, keeping text before and after it
            display_text = (text[:match.start()] + text[match.end():]).strip()
            try:
                suggestion = json.loads(json_str)
                return display_text, suggestion
            except json.JSONDecodeError:
                pass
        return text, None

    def reset_session(self, session_id: str):
        """Xóa lịch sử chat để bắt đầu cuộc trò chuyện mới."""
        with self._lock:
            self.chat_sessions.pop(session_id, None)

    def get_session_count(self):
        with self._lock:
            return len(self.chat_sessions)


# Singleton instance
chatbot_instance = GeminiChatbot()
