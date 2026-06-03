import os
import smtplib
import requests
from concurrent.futures import ThreadPoolExecutor
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config

class EmailService:
    LOG_FILE = os.path.join(Config.DATA_DIR, 'email_notifications.log')
    _executor = ThreadPoolExecutor(max_workers=2)

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
        Send an email via Resend API when configured, otherwise fall back to SMTP Gmail.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body (plain text or HTML)
            template_id: Unused (for compatibility)
            template_params: Unused (for compatibility)
        """
        if Config.RESEND_API_KEY:
            return cls._send_via_resend(to_email, subject, body)

        # Check if SMTP is configured
        if not Config.SMTP_PASSWORD:
            msg_log = f"[EmailService] Email logged (SMTP password not configured) -> {to_email}: {subject}"
            print(msg_log)
            cls._log_email(to_email, subject, body, status="logged_only")
            return True, "Email logged to system (SMTP not configured)."
        
        try:
            print(f"[EmailService] Sending via SMTP to {to_email}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = Config.SMTP_USER
            msg['To'] = to_email
            
            # Attach body
            msg.attach(MIMEText(body, 'html'))
            
            # Connect to Gmail SMTP server and send
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=10) as server:
                server.starttls()  # Upgrade connection to TLS
                server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                server.send_message(msg)
            
            print(f"[EmailService] Email sent successfully via SMTP to {to_email}")
            cls._log_email(to_email, subject, body, status="sent_via_smtp")
            return True, "Email sent successfully!"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "[EmailService] SMTP Authentication failed - check SMTP_PASSWORD"
            print(error_msg)
            cls._log_email(to_email, subject, body, status="auth_failed")
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"[EmailService] SMTP error: {str(e)}"
            print(error_msg)
            cls._log_email(to_email, subject, body, status="smtp_error")
            return False, error_msg
        except Exception as e:
            error_msg = f"[EmailService] Error: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            cls._log_email(to_email, subject, body, status="error")
            return False, error_msg

    @classmethod
    def _send_via_resend(cls, to_email, subject, body):
        """Send email through Resend over HTTPS, which works on Render free instances."""
        try:
            print(f"[EmailService] Sending via Resend to {to_email}")
            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {Config.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": f"{Config.EMAIL_FROM_NAME} <{Config.EMAIL_FROM}>",
                    "to": [to_email],
                    "subject": subject,
                    "html": body.replace("\n", "<br>"),
                    "reply_to": Config.SUPPORT_EMAIL,
                },
                timeout=10,
            )

            if 200 <= response.status_code < 300:
                print(f"[EmailService] Email sent successfully via Resend to {to_email}")
                cls._log_email(to_email, subject, body, status="sent_via_resend")
                return True, "Email sent successfully!"

            error_msg = f"[EmailService] Resend error: {response.status_code} - {response.text}"
            print(error_msg)
            cls._log_email(to_email, subject, body, status="resend_error")
            return False, error_msg
        except requests.Timeout:
            error_msg = "[EmailService] Resend request timeout"
            print(error_msg)
            cls._log_email(to_email, subject, body, status="resend_timeout")
            return False, error_msg
        except Exception as e:
            error_msg = f"[EmailService] Resend error: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            cls._log_email(to_email, subject, body, status="resend_error")
            return False, error_msg

    @classmethod
    def send_email_async(cls, to_email, subject, body, template_id=None, template_params=None):
        """Queue email sending so user-facing requests do not wait on SMTP."""
        if not Config.SEND_EMAIL_ASYNC:
            return cls.send_email(to_email, subject, body, template_id, template_params)
        cls._log_email(to_email, subject, body, status="queued")
        return cls._executor.submit(cls.send_email, to_email, subject, body, template_id, template_params)

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
        
        sender = cls.send_email_async if Config.SEND_EMAIL_ASYNC else cls.send_email
        return sender(
            user_email, 
            subject, 
            body
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
        
        sender = cls.send_email_async if Config.SEND_EMAIL_ASYNC else cls.send_email
        return sender(
            user_email,
            subject,
            body
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
        
        sender = cls.send_email_async if Config.SEND_EMAIL_ASYNC else cls.send_email
        return sender(
            user_email,
            subject,
            body
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
        
        return cls.send_email(
            user_email,
            subject,
            body
        )
