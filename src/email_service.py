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
    def send_email(cls, to_email, subject, body, template_id=None, template_params=None, bypass_emailjs=False):
        """
        Send an email via EmailJS when configured, then Resend, then SMTP Gmail.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body (plain text or HTML)
            template_id: Unused (for compatibility)
            template_params: Unused (for compatibility)
            bypass_emailjs: If True, skips EmailJS and uses Resend/SMTP directly.
        """
        if not bypass_emailjs and Config.EMAILJS_SERVICE_ID and Config.EMAILJS_PUBLIC_KEY and Config.EMAILJS_TEMPLATE_ID:
            ok, message = cls._send_via_emailjs(to_email, subject, body, template_params)
            if ok:
                return ok, message
            print(f"[EmailService] EmailJS failed fallback: {message}")

        if Config.RESEND_API_KEY:
            ok, message = cls._send_via_resend(to_email, subject, body)
            if ok:
                return ok, message
            print(f"[EmailService] Resend failed fallback: {message}")



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
            
            # Attach body — convert plain text to HTML to prevent collapsed lines
            html_body = cls._build_html_body(body)
            msg.attach(MIMEText(html_body, 'html'))
            
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
    def _build_html_body(cls, plain_body: str) -> str:
        """Convert plain text email body to a well-formatted HTML email.
        
        This prevents email clients from collapsing all newlines into a single line.
        Lines starting with '-' are rendered as bold info rows.
        """
        lines = plain_body.strip().split('\n')
        html_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                html_lines.append('<br>')
            elif stripped.startswith('- '):
                # Bold the label before ':' for info lines like "- Bác sĩ: ..."
                content = stripped[2:]
                if ':' in content:
                    label, value = content.split(':', 1)
                    html_lines.append(
                        f'<p style="margin:4px 0;"><strong>{label.strip()}:</strong> {value.strip()}</p>'
                    )
                else:
                    html_lines.append(f'<p style="margin:4px 0;">&bull; {content}</p>')
            else:
                html_lines.append(f'<p style="margin:6px 0;">{stripped}</p>')

        content_html = '\n'.join(html_lines)

        return f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#f4f4f4;margin:0;padding:20px;">
  <div style="max-width:560px;margin:0 auto;background:#ffffff;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.12);">
    <div style="background:linear-gradient(135deg,#1e40af,#3b82f6);padding:24px 28px;">
      <h2 style="margin:0;color:#ffffff;font-size:18px;">🏥 Hệ Thống Đặt Lịch Khám Online</h2>
    </div>
    <div style="padding:28px 28px 20px;line-height:1.7;color:#333333;">
      {content_html}
    </div>
    <div style="background:#f8fafc;padding:14px 28px;text-align:center;font-size:12px;color:#888888;border-top:1px solid #e5e7eb;">
      Đây là email tự động từ hệ thống. Vui lòng không reply trực tiếp vào email này.
    </div>
  </div>
</body>
</html>"""

    @classmethod
    def _send_via_emailjs(cls, to_email, subject, body, template_params=None):
        """Send email through EmailJS over HTTPS."""
        html_body = cls._build_html_body(body)
        params = dict(template_params or {})
        params.update({
            "to_email": to_email,
            "subject": subject,
            "message": html_body,
        })

        try:
            has_private_key = bool(Config.EMAILJS_PRIVATE_KEY)
            print(f"[EmailService] Sending via EmailJS to {to_email} (private_key_configured={has_private_key})")
            payload = {
                "service_id": Config.EMAILJS_SERVICE_ID,
                "template_id": Config.EMAILJS_TEMPLATE_ID,
                "user_id": Config.EMAILJS_PUBLIC_KEY,
                "template_params": params,
            }
            if has_private_key:
                payload["accessToken"] = Config.EMAILJS_PRIVATE_KEY

            response = requests.post(
                Config.EMAILJS_API_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                print(f"[EmailService] Email sent successfully via EmailJS to {to_email}")
                cls._log_email(to_email, subject, body, status="sent_via_emailjs")
                return True, "Email sent successfully!"

            error_msg = f"[EmailService] EmailJS error: {response.status_code} - {response.text}"
            print(error_msg)
            cls._log_email(to_email, subject, body, status="emailjs_error")
            return False, error_msg
        except requests.Timeout:
            error_msg = "[EmailService] EmailJS request timeout"
            print(error_msg)
            cls._log_email(to_email, subject, body, status="emailjs_timeout")
            return False, error_msg
        except Exception as e:
            error_msg = f"[EmailService] EmailJS error: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            cls._log_email(to_email, subject, body, status="emailjs_error")
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
    def send_email_async(cls, to_email, subject, body, template_id=None, template_params=None, bypass_emailjs=False):
        """Queue email sending so user-facing requests do not wait on SMTP.
        
        Always returns (bool, str) — callers can safely unpack the result.
        When async mode is on, the actual send runs in background; this call
        returns (True, 'queued') immediately so the request is not blocked.
        """
        if not Config.SEND_EMAIL_ASYNC:
            return cls.send_email(to_email, subject, body, template_id, template_params, bypass_emailjs=bypass_emailjs)
        cls._log_email(to_email, subject, body, status="queued")
        cls._executor.submit(cls.send_email, to_email, subject, body, template_id, template_params, bypass_emailjs)
        return True, "Email queued for background delivery."

    @classmethod
    def send_booking_confirmation(cls, user_email, user_name, doctor_name, date_str, time_str, clinic_name, address, consultation_fee=None, payment_note=None, **kwargs):
        """Send booking confirmation email."""
        subject = f"[Đặt Lịch Khám] Xác nhận đặt lịch khám thành công - {date_str}"
        
        fee_info = f"\n- Phí khám: {consultation_fee}" if consultation_fee else ""
        payment_info = f"\n- Ghi chú: {payment_note}" if payment_note else ""
        
        body = f"""Chào {user_name},

Chúc mừng bạn đã đặt lịch khám thành công qua hệ thống Đặt Lịch Khám Online!

Chi tiết lịch hẹn của bạn:
- Bác sĩ: {doctor_name}
- Ngày khám: {date_str}
- Khung giờ: {time_str}
- Phòng khám: {clinic_name}
- Địa chỉ: {address}{fee_info}{payment_info}

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
            "consultation_fee": consultation_fee if consultation_fee else "Theo quy định phòng khám",
            "payment_note": payment_note if payment_note else "",
            "message": body
        }
        
        # bypass_emailjs=True: EmailJS Free Plan only reliably delivers to the account owner's
        # email. SMTP Gmail sends to any user email correctly.
        return cls.send_email(
            user_email,
            subject,
            body,
            template_params=template_params,
            bypass_emailjs=True
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
            "message": body,
        }

        return cls.send_email(
            user_email,
            subject,
            body,
            template_params=template_params,
            bypass_emailjs=True
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
            "message": body,
        }

        return cls.send_email(
            user_email,
            subject,
            body,
            template_params=template_params,
            bypass_emailjs=True
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
            "message": body,
        }

        return cls.send_email(
            user_email,
            subject,
            body,
            template_params=template_params,
            bypass_emailjs=True
        )

    @classmethod
    def send_welcome_email(cls, user_email: str, user_name: str):
        """Send a welcome email immediately after successful registration."""
        subject = "[MedBooking] Chao mung ban den voi Dat Lich Kham Online!"
        body = f"""Chao {user_name},

Tai khoan cua ban da duoc tao thanh cong tren he thong Dat Lich Kham Online!

Thong tin tai khoan:
- Ho ten: {user_name}
- Email dang nhap: {user_email}

Voi tai khoan nay, ban co the:
- Tim kiem bac si theo trieu chung hoac chuyen khoa
- Dat lich kham truc tuyen nhanh chong
- Quan ly lich hen tren trang ca nhan (Dashboard)
- Nhan email nhac nho truoc lich kham

Luu y: Day la email tu dong. Vui long khong reply truc tiep vao email nay.
Neu can ho tro, vui long lien he qua email: {Config.SUPPORT_EMAIL}

Cam on ban da tin tuong su dung dich vu cua chung toi!
He thong Dat Lich Kham Online.
"""
        template_params = {
            "to_email": user_email,
            "user_name": user_name,
            "message": body,
        }
        # bypass_emailjs=True because the EmailJS template is designed for booking confirmations,
        # not welcome emails. Sending directly via SMTP/Resend ensures the correct content.
        return cls.send_email(user_email, subject, body, template_params=template_params, bypass_emailjs=True)

