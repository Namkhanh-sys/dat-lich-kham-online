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

# Prompt hệ thống — định nghĩa vai trò chatbot
SYSTEM_PROMPT = """Bạn là trợ lý y tế AI của hệ thống đặt lịch khám trực tuyến tại Việt Nam.

NHIỆM VỤ CHÍNH:
Hỏi từng câu một để thu thập đủ thông tin, rồi mới đưa ra nhận định chuyên khoa phù hợp.

⚠️ CẢNH BÁO QUAN TRỌNG:
1. MỖI LẦN CHỈ ĐƯỢC HỎI DUY NHẤT 1 CÂU HỎI. Không được hỏi gộp nhiều câu cùng lúc.
2. BẤT KỲ CÂU HỎI NÀO CỦA BẠN CŨNG BẮT BUỘC PHẢI CÓ gợi ý câu trả lời dưới dạng OPTIONS ở cuối tin nhắn. Cấm tuyệt đối việc đặt câu hỏi mà không có OPTIONS.

══════════════════════════════════════════
QUY TRÌNH BẮT BUỘC — PHẢI TUÂN THỦ NGHIÊM NGẶT:

BƯỚC 1 — NHẬN TRIỆU CHỨNG BAN ĐẦU:
  Người dùng nói triệu chứng → bạn hỏi ngay 1 câu làm rõ (thời gian, mức độ, vị trí...).
  TUYỆT ĐỐI KHÔNG được đưa ra kết luận ở bước này.
  BẮT BUỘC đi kèm OPTIONS tương ứng.

BƯỚC 2 — HỎI THÊM (ít nhất 2 lần hỏi):
  Sau mỗi câu trả lời của người dùng, hỏi thêm 1 câu cụ thể hơn.
  Mỗi lượt chỉ hỏi 1 câu duy nhất và BẮT BUỘC đi kèm OPTIONS.
  Ví dụ các câu hỏi tốt:
  • "Cơn đau xuất hiện từ bao lâu rồi?"  OPTIONS:["Vài giờ nay","1–2 ngày","Hơn 3 ngày","Tái đi tái lại nhiều lần"]
  • "Đau ở vị trí nào trong ngực?"       OPTIONS:["Ngực trái","Ngực phải","Giữa ngực","Toàn bộ ngực"]
  • "Ngoài đau ngực, bạn còn có triệu chứng nào khác không?" OPTIONS:["Khó thở, hụt hơi","Hồi hộp, tim đập nhanh","Buồn nôn, chóng mặt","Chỉ đau ngực thôi"]
  • "Cơn đau có liên quan đến vận động không?" OPTIONS:["Đau nhiều hơn khi vận động","Đau kể cả khi nghỉ ngơi","Đau khi hít thở sâu","Không rõ"]

BƯỚC 3 — KẾT LUẬN (chỉ sau ≥ 2 lượt hỏi–đáp):
  Khi đã có đủ thông tin, đưa ra phân tích và thêm DOCTOR_SUGGESTION.
  (Không được kèm OPTIONS ở bước kết luận này).

══════════════════════════════════════════
FORMAT CÂU HỎI — dùng OPTIONS ở cuối tin nhắn:
Nội dung câu hỏi của bạn.
OPTIONS:["lựa chọn 1","lựa chọn 2","lựa chọn 3"]

FORMAT KẾT LUẬN — thêm vào CUỐI tin nhắn kết luận:
DOCTOR_SUGGESTION:{"specialty":"<tên chuyên khoa>","keywords":"<từ khóa triệu chứng tiếng Việt>","advice":"<1 câu lời khuyên ngắn>"}

Chuyên khoa thường dùng: Tim mạch, Thần kinh, Tiêu hóa, Hô hấp, Cơ xương khớp, Da liễu, Tai mũi họng, Mắt, Nội tiết, Tiết niệu.

══════════════════════════════════════════
PHONG CÁCH KẾT LUẬN:

❌ SAI — rập khuôn, vô nghĩa:
"Dựa trên thông tin bạn cung cấp, có thể bạn cần khám tại chuyên khoa Tim mạch hoặc Hô hấp."
"Tình trạng của bạn có thể liên quan đến các vấn đề về tim mạch."

✅ ĐÚNG — phân tích cụ thể, ân cần:
"Cơn đau ngực trái kéo dài 2 ngày, tăng khi vận động và kèm theo hồi hộp là những dấu hiệu cần được đánh giá kỹ về chức năng tim. Đây có thể là biểu hiện của rối loạn nhịp tim hoặc co thắt mạch vành. Bạn nên đến khám chuyên khoa Tim mạch sớm để được điện tâm đồ và tư vấn chính xác."

══════════════════════════════════════════
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
            self.model_name = 'gemini-2.0-flash'  # 200 RPD free tier (vs 20 RPD for 2.5-flash-lite)
            # chat_sessions: OrderedDict làm LRU cache tự chế tránh tràn RAM
            self.chat_sessions = OrderedDict()
            self.max_sessions = 1000  # Lưu tối đa 1000 phiên hoạt động gần nhất
            self.max_history_len = 10  # Giữ tối đa 10 tin nhắn gần nhất để tiết kiệm token đầu vào
            self._initialized = True
            self._available = True
        except Exception as e:
            print(f"[CHATBOT] Gemini init error: {e}")
            self._available = False

    @property
    def is_available(self):
        groq_key = getattr(Config, 'GROQ_API_KEY', '')
        gemini_key = getattr(Config, 'GEMINI_API_KEY', '')
        
        has_groq = bool(groq_key) and groq_key.strip() not in ('', 'PASTE_YOUR_KEY_HERE')
        has_gemini = getattr(self, '_available', False) and bool(gemini_key) and gemini_key.strip() not in ('', 'PASTE_YOUR_KEY_HERE')
        
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
            if user_msg_count >= 5:
                active_prompt += "\n\n⚠️ YÊU CẦU BẮT BUỘC: Bạn đã hỏi người dùng đủ 5 câu hỏi. KHÔNG ĐƯỢC HỎI THÊM NỮA. Hãy đưa ra kết luận phân tích triệu chứng chi tiết và gợi ý chuyên khoa phù hợp dưới dạng DOCTOR_SUGGESTION ngay trong tin nhắn này. Tuyệt đối KHÔNG xuất hiện OPTIONS."

            full_reply = None

            # 1. Thử gọi Groq Cloud API nếu có Key hoạt động
            groq_key = getattr(Config, 'GROQ_API_KEY', '')
            if bool(groq_key) and groq_key.strip() not in ('', 'PASTE_YOUR_KEY_HERE'):
                try:
                    import requests
                    import time
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
                    for _attempt in range(2):  # 1 retry on 429
                        response = requests.post(
                            "https://api.groq.com/openai/v1/chat/completions",
                            headers=headers,
                            json=payload,
                            timeout=15
                        )
                        if response.status_code == 200:
                            res_data = response.json()
                            full_reply = res_data["choices"][0]["message"]["content"]
                            break
                        elif response.status_code == 429 and _attempt == 0:
                            # Respect Retry-After header; cap wait at 8 s to stay within request timeout
                            retry_after = float(response.headers.get('Retry-After', '5'))
                            wait_secs = min(retry_after + 0.5, 8.0)
                            print(f"[CHATBOT] Groq 429 — retrying in {wait_secs:.1f}s...")
                            time.sleep(wait_secs)
                        else:
                            print(f"[CHATBOT] Groq error status: {response.status_code}, response: {response.text}")
                            break
                except Exception as groq_err:
                    print(f"[CHATBOT] Groq call failed: {groq_err}. Falling back to Gemini...")

            # 2. Dự phòng: Gọi Google Gemini API nếu Groq không khả dụng hoặc gặp lỗi
            if full_reply is None:
                gemini_key = getattr(Config, 'GEMINI_API_KEY', '')
                if getattr(self, '_available', False) and bool(gemini_key) and gemini_key.strip() not in ('', 'PASTE_YOUR_KEY_HERE'):
                    # Chuyển đổi lịch sử sang định dạng Content của SDK Gemini
                    gemini_history = []
                    for h in history:
                        role = "model" if h["role"] == "assistant" else h["role"]
                        gemini_history.append(
                            types.Content(
                                role=role,
                                parts=[types.Part(text=h["content"])]
                            )
                        )
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=gemini_history,
                        config=types.GenerateContentConfig(
                            system_instruction=active_prompt,
                            temperature=0.85,
                            max_output_tokens=400,
                        )
                    )
                    full_reply = response.text

            if full_reply is None:
                raise Exception("Tất cả các API Engine (Groq, Gemini) đều không khả dụng hoặc gặp lỗi cuộc gọi.")

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
