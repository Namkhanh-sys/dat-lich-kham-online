import os
from datetime import datetime
from config import Config

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    HAS_SENDGRID = True
except ImportError:
    HAS_SENDGRID = False

class EmailService:
    LOG_FILE = os.path.join(Config.DATA_DIR, 'email_notifications.log')

    @classmethod
    def _log_mock_email(cls, to_email, subject, body):
        """Write the email content to a local log file for testing/mocking."""
        try:
            os.makedirs(os.path.dirname(cls.LOG_FILE), exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(cls.LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"=== EMAIL SENT AT {timestamp} ===\n")
                f.write(f"To: {to_email}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Body:\n{body}\n")
                f.write("="*40 + "\n\n")
            return True
        except Exception as e:
            print(f"Error logging mock email: {e}")
            return False

    @classmethod
    def send_email(cls, to_email, subject, body):
        """
        Send an email via SendGrid API.
        Falls back to file logging if API key not configured.
        """
        # Always log to file for audit trail
        cls._log_mock_email(to_email, subject, body)
        
        # If SendGrid API key not configured, use file logging only
        if not Config.SENDGRID_API_KEY or not HAS_SENDGRID:
            msg_log = f"[EmailService] Email logged (no SendGrid key configured) -> {to_email}: {subject}"
            print(msg_log)
            return True, "Confirmation saved to system."
        
        try:
            print(f"[EmailService] Sending via SendGrid to {to_email}")
            
            # Create email
            message = Mail(
                from_email=(Config.EMAIL_FROM, Config.EMAIL_FROM_NAME),
                to_emails=to_email,
                subject=subject,
                plain_text_content=body
            )
            
            # Send via SendGrid API
            sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
            response = sg.send(message)
            
            print(f"[EmailService] Email sent successfully, status_code={response.status_code}")
            return True, "Email sent successfully!"
            
        except Exception as e:
            error_msg = f"[EmailService] SendGrid error: {str(e)}"
            print(error_msg)
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
        return cls.send_email(user_email, subject, body)

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
        return cls.send_email(user_email, subject, body)

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
        return cls.send_email(user_email, subject, body)

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
Hệ thống Đặt Lịch Khám Online.
"""
        return cls.send_email(user_email, subject, body)
