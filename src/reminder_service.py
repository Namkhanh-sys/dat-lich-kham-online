import threading
import time
import pandas as pd
from datetime import datetime, timedelta
from src.csv_helper import CSVHelper
from src.email_service import EmailService

class ReminderService:
    @staticmethod
    def check_and_send_reminders():
        while True:
            try:
                df_app = CSVHelper.get_appointments()
                df_users = CSVHelper.get_users()
                df_docs = CSVHelper.get_doctors()
                df_clinics = CSVHelper.get_clinics()

                if not df_app.empty and not df_users.empty and not df_docs.empty:
                    # Initialize reminder_sent column if it doesn't exist
                    if 'reminder_sent' not in df_app.columns:
                        df_app['reminder_sent'] = 'False'
                        
                    now = datetime.now()
                    # BUG FIX #8: Use a full datetime window (now → now+24h) instead of comparing
                    # only the date, which could miss late-night appointments or include ones
                    # that are actually more than 24 hours away.
                    target_from = now
                    target_to = now + timedelta(hours=24)

                    # Pre-filter: status is not cancelled, reminder not sent
                    mask = (df_app['status'].str.strip() != 'Đã hủy') & \
                           (df_app['reminder_sent'] != 'True')

                    appointments_to_remind = df_app[mask]
                    changed = False
                    
                    for idx, row in appointments_to_remind.iterrows():
                        # BUG FIX #8: Check that the appointment datetime falls within the 24h window
                        try:
                            appt_dt = datetime.strptime(f"{row['date']} {row['time']}", "%Y-%m-%d %H:%M")
                        except ValueError:
                            continue
                        if not (target_from <= appt_dt <= target_to):
                            continue

                        user_id = row['user_id']
                        doctor_id = row['doctor_id']
                        
                        user_row = df_users[df_users['id'] == user_id]
                        doc_row = df_docs[df_docs['id'] == doctor_id]
                        
                        if not user_row.empty and not doc_row.empty:
                            user = user_row.iloc[0].to_dict()
                            doc = doc_row.iloc[0].to_dict()
                            clinic_row = df_clinics[df_clinics['id'].str.strip() == str(doc.get('clinic_id', '')).strip()]
                            clinic = clinic_row.iloc[0].to_dict() if not clinic_row.empty else {}
                            
                            EmailService.send_booking_reminder(
                                user_email=user['email'],
                                user_name=user['name'],
                                doctor_name=doc['name'],
                                date_str=row['date'],
                                time_str=row['time'],
                                clinic_name=clinic.get('name', 'Phòng khám chưa xác định'),
                                address=clinic.get('address', 'Chưa có địa chỉ')
                            )
                            
                            # Mark as reminded
                            df_app.at[idx, 'reminder_sent'] = 'True'
                            changed = True
                            
                    if changed:
                        CSVHelper.save_appointments(df_app)
                        print(f"[ReminderService] Sent reminders and updated CSV.")

            except Exception as e:
                print(f"[ReminderService] Error: {e}")

            # Sleep for 1 hour before checking again
            time.sleep(3600)

    @classmethod
    def start_background_task(cls):
        """Starts the background thread that polls for upcoming appointments."""
        thread = threading.Thread(target=cls.check_and_send_reminders, daemon=True)
        thread.start()
        print("[ReminderService] Background thread started.")
