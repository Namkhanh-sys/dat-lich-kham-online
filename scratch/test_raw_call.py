import os
from google import genai
from google.genai import types

# Read key from .env manually
key = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                key = line.split("=", 1)[1].strip()
                break

client = genai.Client(api_key=key)

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

active_prompt = SYSTEM_PROMPT + "\n\n⚠️ YÊU CẦU BẮT BUỘC: Bạn đã thu thập đủ thông tin (qua 3 tin nhắn của người dùng). KHÔNG ĐƯỢC HỎI THÊM NỮA. Hãy đưa ra kết luận phân tích triệu chứng chi tiết và gợi ý chuyên khoa phù hợp dưới dạng DOCTOR_SUGGESTION ngay trong tin nhắn này. Tuyệt đối KHÔNG xuất hiện OPTIONS."

history = [
    {"role": "assistant", "content": "Xin chào! Tôi là trợ lý y tế AI 🏥... Bạn đang gặp phải vấn đề sức khỏe gì?"},
    {"role": "user", "content": "Tôi bị đau dạ dày"},
    {"role": "assistant", "content": "Chào bạn, đau dạ dày thường xuất hiện vào thời điểm nào trong ngày hoặc có liên quan đến bữa ăn không?\nOPTIONS:[\"Trước khi ăn\",\"Sau khi ăn\",\"Khi đói\",\"Không liên quan\"]"},
    {"role": "user", "content": "Vài ngày"},
    {"role": "assistant", "content": "Đau dạ dày của bạn có kèm theo các triệu chứng khác như buồn nôn, nôn, hoặc tiêu chảy không?\nOPTIONS:[\"Có\",\"Không\",\"Thỉnh thoảng\"]"},
    {"role": "user", "content": "Có, tôi bị chán ăn."}
]

gemini_history = []
for h in history:
    role = "model" if h["role"] == "assistant" else h["role"]
    gemini_history.append(
        types.Content(role=role, parts=[types.Part(text=h["content"])])
    )

print("--- Experiment 1: Single prompt text (no contents list, no system_instruction) ---")
prompt_text = f"""{active_prompt}

Lịch sử trò chuyện:
"""
for h in history:
    role_name = "Trợ lý" if h["role"] == "assistant" else "Người dùng"
    prompt_text += f"{role_name}: {h['content']}\n"

prompt_text += "Trợ lý:"

try:
    resp = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt_text,
        config=types.GenerateContentConfig(
            temperature=0.85,
            max_output_tokens=600,
        )
    )
    print("Experiment 1 text:", repr(resp.text))
    print("Finish reason:", resp.candidates[0].finish_reason if resp.candidates else "No candidates")
except Exception as e:
    print("Experiment 1 failed:", e)


print("\n--- Experiment 2: contents list with first message as user (alternating) ---")
alt_history = history[1:]  # Start with user: "Tôi bị đau dạ dày"
gemini_history_alt = []
for h in alt_history:
    role = "model" if h["role"] == "assistant" else h["role"]
    gemini_history_alt.append(
        types.Content(role=role, parts=[types.Part(text=h["content"])])
    )

try:
    resp = client.models.generate_content(
        model='gemini-flash-latest',
        contents=gemini_history_alt,
        config=types.GenerateContentConfig(
            system_instruction=active_prompt,
            temperature=0.85,
            max_output_tokens=600,
        )
    )
    print("Experiment 2 text:", repr(resp.text))
    print("Finish reason:", resp.candidates[0].finish_reason if resp.candidates else "No candidates")
except Exception as e:
    print("Experiment 2 failed:", e)

