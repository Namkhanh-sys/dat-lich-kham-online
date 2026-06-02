import os
import requests
from datetime import datetime
from config import Config

class EmailService:
    LOG_FILE = os.path.join(Config.DATA_DIR, 'email_notifications.log')

    @classmethod
    def _log_email(cls, to_email, subject, body, status="sent"):
        """Log email activity to a local file for audit trail."""
        try:
            os.makedirs(os.path.dirname(cls.LOG_FILE), exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(cls.LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"=== EMAIL {status.upper()} AT {timestamp} ===\n")
                f.write(f"To: {to_email}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Body:\n{body}\n")
                f.write("="*40 + "\n\n")
            return True
        except Exception as e:
            print(f"Error logging email: {e}")
            return False

    @classmethod
    def send_email(cls, to_email, subject, body, template_id=None, template_params=None):
        """
        Send an email via EmailJS API.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body (plain text or HTML)
            template_id: EmailJS template ID (optional, if using templates)
            template_params: Dictionary of template parameters (optional)
        """
        # Always log to file for audit trail
        cls._log_email(to_email, subject, body)
        
        # Check if EmailJS credentials are configured
        if not Config.EMAILJS_SERVICE_ID or not Config.EMAILJS_PUBLIC_KEY:
            msg_log = f"[EmailService] Email logged (EmailJS not configured) -> {to_email}: {subject}"
            print(msg_log)
            return True, "Email logged to system."
        
        try:
            print(f"[EmailService] Sending via EmailJS to {to_email}")
            
            # Prepare payload for EmailJS
            if template_id and template_params:
                # Send using template
                payload = {
                    "service_id": Config.EMAILJS_SERVICE_ID,
                    "template_id": template_id,
                    "user_id": Config.EMAILJS_PUBLIC_KEY,
                    "template_params": template_params
                }
            else:
                # Send plain email
                payload = {
                    "service_id": Config.EMAILJS_SERVICE_ID,
                    "template_id": "plain_email",  # You need to create this template
                    "user_id": Config.EMAILJS_PUBLIC_KEY,
                    "template_params": {
                        "to_email": to_email,
                        "subject": subject,
                        "message": body
                    }
                }
            
            # Send request to EmailJS API
            response = requests.post(
                Config.EMAILJS_API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"[EmailService] Email sent successfully via EmailJS")
                cls._log_email(to_email, subject, body, status="sent_via_emailjs")
                return True, "Email sent successfully!"
            else:
                error_msg = f"[EmailService] EmailJS error: {response.status_code} - {response.text}"
                print(error_msg)
                cls._log_email(to_email, subject, body, status="failed")
                return False, error_msg
                
        except requests.Timeout:
            error_msg = "[EmailService] EmailJS request timeout"
            print(error_msg)
            cls._log_email(to_email, subject, body, status="timeout")
            return False, error_msg
        except Exception as e:
            error_msg = f"[EmailService] Error: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            cls._log_email(to_email, subject, body, status="error")
            return False, error_msg

    @classmethod
    def send_booking_confirmation(cls, user_email, user_name, doctor_name, date_str, time_str, clinic_name, address):
        """Send booking confirmation email."""
        subject = f"[Đặt Lịch Khám] Xác nhận đặt lịch khám thành công - {date_str}"
        body = f"""Chào {user_name},

Chúc mừng bạn đã đặt lịch khám thành công qua hệ thống Đặt Lịch Khám Online!

Chi tiết lịch hẹn của bạn:
- Bác sĩ: {doctor_name}
- Ngày khám: {date_str}
- Khung giờ: {time_str}
- Phòng khám: {clinic_name}
- Địa chỉ: {address}

Lưu ý: Vui lòng đến trước giờ hẹn 10-15 phút để làm thủ tục check-in. Nếu muốn thay đổi hoặc hủy lịch, vui lòng thực hiện trên Dashboard cá nhân trước ít nhất 2 tiếng.

Cảm ơn bạn đã tin tưởng dịch vụ của chúng tôi!
Hệ thống Đặt Lịch Khám Online.
"""
        template_params = {
            "to_email": user_email,
            "user_name": user_name,
            "doctor_name": doctor_name,
            "date_str": date_str,
            "time_str": time_str,
            "clinic_name": clinic_name,
            "address": address,
            "message": body
        }
        
        return cls.send_email(
            user_email, 
            subject, 
            body,
            template_id=Config.EMAILJS_TEMPLATE_ID,
            template_params=template_params
        )

    @classmethod
    def send_booking_update(cls, user_email, user_name, doctor_name, date_str, time_str, clinic_name, address):
        """Send booking rescheduling update email."""
        subject = f"[Đặt Lịch Khám] Thay đổi thời gian lịch hẹn thành công"
        body = f"""Chào {user_name},

Lịch hẹn khám bệnh của bạn đã được cập nhật thành công thời gian mới.

Chi tiết lịch hẹn mới:
- Bác sĩ: {doctor_name}
- Ngày khám: {date_str}
- Khung giờ: {time_str}
- Phòng khám: {clinic_name}
- Địa chỉ: {address}

Cảm ơn bạn đã tin tưởng dịch vụ của chúng tôi!
Hệ thống Đặt Lịch Khám Online.
"""
        template_params = {
            "to_email": user_email,
            "user_name": user_name,
            "doctor_name": doctor_name,
            "date_str": date_str,
            "time_str": time_str,
            "clinic_name": clinic_name,
            "address": address,
            "message": body
        }
        
        return cls.send_email(
            user_email,
            subject,
            body,
            template_id=Config.EMAILJS_TEMPLATE_ID,
            template_params=template_params
        )

    @classmethod
    def send_booking_cancellation(cls, user_email, user_name, doctor_name, date_str, time_str):
        """Send booking cancellation email."""
        subject = f"[Đặt Lịch Khám] Thông báo hủy lịch hẹn thành công"
        body = f"""Chào {user_name},

Hệ thống xác nhận bạn đã hủy thành công lịch hẹn khám bệnh sau:
- Bác sĩ: {doctor_name}
- Ngày khám: {date_str}
- Khung giờ: {time_str}

Số tiền hoặc chi phí (nếu có) sẽ được giải quyết theo chính sách phòng khám. Rất tiếc vì chưa được phục vụ bạn lần này!

Hệ thống Đặt Lịch Khám Online.
"""
        template_params = {
            "to_email": user_email,
            "user_name": user_name,
            "doctor_name": doctor_name,
            "date_str": date_str,
            "time_str": time_str,
            "message": body
        }
        
        return cls.send_email(
            user_email,
            subject,
            body,
            template_id=Config.EMAILJS_TEMPLATE_ID,
            template_params=template_params
        )

    @classmethod
    def send_booking_reminder(cls, user_email, user_name, doctor_name, date_str, time_str, clinic_name, address):
        """Send automated reminder email 24 hours before the appointment."""
        subject = f"[Nhắc Lịch Khám] Lịch khám của bạn vào ngày mai ({date_str})"
        body = f"""Chào {user_name},

Hệ thống Đặt Lịch Khám Online xin nhắc nhở bạn về lịch hẹn khám bệnh sắp tới:
- Bác sĩ: {doctor_name}
- Ngày khám: {date_str}
- Khung giờ: {time_str}
- Phòng khám: {clinic_name}
- Địa chỉ: {address}

Vui lòng có mặt tại phòng khám trước giờ hẹn 10-15 phút để làm thủ tục. 
Nếu bạn có thay đổi lịch trình, vui lòng truy cập Dashboard để đổi hoặc hủy lịch sớm nhất có thể.

Chúc bạn nhiều sức khỏe,
Hệ thống Đặt Lịch Khám Online."""
        
        template_params = {
            "to_email": user_email,
            "user_name": user_name,
            "doctor_name": doctor_name,
            "date_str": date_str,
            "time_str": time_str,
            "clinic_name": clinic_name,
            "address": address,
            "message": body
        }
        
        return cls.send_email(
            user_email,
            subject,
            body,
            template_id=Config.EMAILJS_TEMPLATE_ID,
            template_params=template_params
        )
