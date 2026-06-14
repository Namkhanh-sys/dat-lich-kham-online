import uuid
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
from src.csv_helper import CSVHelper

class BookingManager:
    STANDARD_SLOTS: List[str] = [
        '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00'
    ]
    # Giới hạn số lịch khám tối đa một người dùng có thể đặt trong cùng 1 ngày
    MAX_BOOKINGS_PER_DAY: int = 2
    # Lock bảo vệ toàn bộ chuỗi kiểm tra trùng lịch → ghi file khỏi race condition
    _booking_lock: threading.Lock = threading.Lock()

    @classmethod
    def get_doctor_appointments_on_date(cls, doctor_id: str, date_str: str) -> List[str]:
        """Get all appointments for a doctor on a specific date."""
        df = CSVHelper.get_appointments()
        if df.empty:
            return []
        
        # Filter by doctor_id, date, and make sure it is not cancelled
        active_appointments = df[
            (df['doctor_id'] == doctor_id) & 
            (df['date'] == date_str) & 
            (df['status'].str.strip() != 'Đã hủy')
        ]
        return active_appointments['time'].tolist()

    @classmethod
    def check_collision(cls, doctor_id: str, date_str: str, time_str: str) -> bool:
        """Check if the doctor is already booked at this date and time."""
        booked_slots = cls.get_doctor_appointments_on_date(doctor_id, date_str)
        return time_str in booked_slots

    @classmethod
    def check_user_collision(cls, user_id: str, date_str: str, time_str: str, exclude_appointment_id: Optional[str] = None) -> bool:
        """Check if a user already has an active appointment at this exact date and time (with any doctor)."""
        df = CSVHelper.get_appointments()
        if df.empty:
            return False
        mask = (
            (df['user_id'] == user_id) &
            (df['date'] == date_str) &
            (df['time'] == time_str) &
            (df['status'].str.strip() != 'Đã hủy')
        )
        if exclude_appointment_id:
            mask = mask & (df['id'] != exclude_appointment_id)
        return mask.any()

    @classmethod
    def count_user_bookings_on_date(cls, user_id: str, date_str: str, df: Optional[pd.DataFrame] = None) -> int:
        """Count how many active (non-cancelled) appointments the user has on a specific date.
        
        Accepts an optional pre-loaded DataFrame so callers inside the lock can
        reuse the same snapshot instead of re-reading the CSV.
        """
        if df is None:
            df = CSVHelper.get_appointments()
        if df.empty:
            return 0
        mask = (
            (df['user_id'] == user_id) &
            (df['date'] == date_str) &
            (df['status'].str.strip() != 'Đã hủy')
        )
        return int(mask.sum())

    @classmethod
    def _available_slots(cls, booked_slots: List[str], date_str: str, limit: Optional[int] = None) -> List[str]:
        """Return standard slots not in booked_slots, excluding past times for today."""
        available_slots = [slot for slot in cls.STANDARD_SLOTS if slot not in booked_slots]
        today_str = datetime.today().strftime('%Y-%m-%d')
        if date_str == today_str:
            now_time = datetime.now().strftime('%H:%M')
            available_slots = [s for s in available_slots if s > now_time]
        if limit is not None:
            return available_slots[:limit]
        return available_slots

    @classmethod
    def suggest_alternative_slots(cls, doctor_id: str, date_str: str, limit: int = 3, days_checked: int = 1) -> List[str]:
        """Suggest available alternative time slots for a doctor on a specific date."""
        booked_slots = cls.get_doctor_appointments_on_date(doctor_id, date_str)
        available_slots = cls._available_slots(booked_slots, date_str)
        
        # If there are no slots on this date, we could recommend slots on the next day
        if not available_slots:
            if days_checked >= 7:
                return []  # Prevent infinite recursion by limiting lookahead to 7 days
            try:
                current_date = datetime.strptime(date_str, "%Y-%m-%d")
                next_date = current_date + timedelta(days=1)
                next_date_str = next_date.strftime("%Y-%m-%d")
                return cls.suggest_alternative_slots(doctor_id, next_date_str, limit, days_checked + 1)
            except ValueError:
                pass
                
        return available_slots[:limit]

    @classmethod
    def create_booking(cls, user_id: str, doctor_id: str, date_str: str, time_str: str) -> Tuple[bool, Union[Dict[str, Any], str]]:
        """Create a new booking if no collision. Returns (success, message_or_appointment_dict).
        
        Uses _booking_lock to make the entire check→write sequence atomic,
        preventing two concurrent requests from both passing the collision check
        for the same doctor+date+time slot (race condition).
        """
        print(f"[BookingManager.create_booking] START: user={user_id}, doctor={doctor_id}, date={date_str}, time={time_str}")
        
        # Validate date and time format BEFORE acquiring the lock (no I/O needed)
        try:
            appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if appt_date < datetime.today().date():
                print(f"[BookingManager.create_booking] Date is in the past")
                return False, "Không thể đặt lịch cho ngày đã qua."
            # BUG FIX #1: Also reject time slots that have already passed on today's date
            if appt_date == datetime.today().date() and time_str <= datetime.now().strftime('%H:%M'):
                print(f"[BookingManager.create_booking] Time has already passed today")
                return False, "Không thể đặt lịch cho khung giờ đã qua trong ngày hôm nay."
            if time_str not in cls.STANDARD_SLOTS:
                print(f"[BookingManager.create_booking] Invalid time slot: {time_str}")
                return False, "Khung giờ khám không hợp lệ."
        except ValueError as e:
            print(f"[BookingManager.create_booking] Date format error: {e}")
            return False, "Định dạng ngày khám không hợp lệ (hãy dùng YYYY-MM-DD)."

        # ──── CRITICAL SECTION: chỉ 1 request được chạy qua đây tại một thời điểm ────
        with cls._booking_lock:
            # — Tải dữ liệu 1 lần duy nhất trong lock để đảm bảo snapshot nhất quán
            df_appointments = CSVHelper.get_appointments()

            # Check collision — bác sĩ đã có lịch giờ này
            print(f"[BookingManager.create_booking] [LOCKED] Checking doctor collision...")
            booked_slots = df_appointments[
                (df_appointments['doctor_id'] == doctor_id) &
                (df_appointments['date'] == date_str) &
                (df_appointments['status'].str.strip() != 'Đã hủy')
            ]['time'].tolist()
            if time_str in booked_slots:
                alternatives = cls.suggest_alternative_slots(doctor_id, date_str)
                alt_str = ", ".join(alternatives)
                print(f"[BookingManager.create_booking] Doctor collision detected")
                return False, f"Bác sĩ đã có lịch hẹn vào giờ này. Vui lòng chọn giờ khác. Gợi ý giờ trống: {alt_str}."

            # Check user collision — người dùng đã có lịch khám cùng giờ với bác sĩ khác
            print(f"[BookingManager.create_booking] [LOCKED] Checking user collision...")
            user_same_time = (
                (df_appointments['user_id'] == user_id) &
                (df_appointments['date'] == date_str) &
                (df_appointments['time'] == time_str) &
                (df_appointments['status'].str.strip() != 'Đã hủy')
            )
            if user_same_time.any():
                print(f"[BookingManager.create_booking] User already has appointment at this time")
                return False, f"Bạn đã có lịch khám vào {time_str} ngày {date_str} với một bác sĩ khác. Vui lòng chọn khung giờ khác."

            print(f"[BookingManager.create_booking] [LOCKED] No collision, creating appointment...")
            print(f"[BookingManager.create_booking] Current appointments count: {len(df_appointments)}")
            
            appointment_id = f"a_{uuid.uuid4().hex[:8]}"
            
            new_appointment = {
                'id': appointment_id,
                'user_id': user_id,
                'doctor_id': doctor_id,
                'date': date_str,
                'time': time_str,
                'status': 'Đã xác nhận'
            }
            print(f"[BookingManager.create_booking] Created appointment dict: {new_appointment}")

            if df_appointments.empty:
                df_appointments = pd.DataFrame([new_appointment])
            else:
                df_appointments = pd.concat([df_appointments, pd.DataFrame([new_appointment])], ignore_index=True)
            
            print(f"[BookingManager.create_booking] Saving to CSV...")
            if CSVHelper.save_appointments(df_appointments):
                print(f"[BookingManager.create_booking] SUCCESS: Appointment saved with id={appointment_id}")
                return True, new_appointment
            
            print(f"[BookingManager.create_booking] FAILED: Could not save appointment")
            return False, "Lỗi hệ thống khi lưu lịch hẹn."

    @classmethod
    def get_user_appointments(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get all appointments for a user, joined with doctor and clinic details."""
        df_app = CSVHelper.get_appointments()
        if df_app.empty:
            return []

        # Filter appointments of the user
        user_apps = df_app[df_app['user_id'] == user_id].copy()
        if user_apps.empty:
            return []

        df_docs = CSVHelper.get_doctors()
        df_clinics = CSVHelper.get_clinics()

        # Join doctor and clinic info
        merged = user_apps.merge(df_docs, left_on='doctor_id', right_on='id', suffixes=('', '_doc'))
        if not df_clinics.empty:
            merged = merged.merge(df_clinics, left_on='clinic_id', right_on='id', suffixes=('', '_clinic'))

        # Sort by date and time
        merged['datetime'] = pd.to_datetime(merged['date'] + ' ' + merged['time'])
        merged = merged.sort_values(by='datetime', ascending=True)
        merged = merged.drop(columns=['datetime'])

        # Rename columns to avoid confusion
        rename_dict = {
            'name': 'doctor_name',
            'name_clinic': 'clinic_name',
            'address': 'clinic_address'
        }
        merged = merged.rename(columns=rename_dict)
        
        return merged.to_dict('records')

    @classmethod
    def cancel_booking(cls, appointment_id: str, user_id: str) -> Tuple[bool, str]:
        """Cancel an existing booking."""
        df = CSVHelper.get_appointments()
        if df.empty:
            return False, "Không tìm thấy dữ liệu lịch hẹn."

        mask = (df['id'] == appointment_id) & (df['user_id'] == user_id)
        if not mask.any():
            return False, "Lịch hẹn không tồn tại hoặc không thuộc quyền sở hữu của bạn."

        # BUG FIX #5: Prevent cancelling an already-cancelled appointment
        current_status = df.loc[mask, 'status'].values[0].strip()
        if current_status == 'Đã hủy':
            return False, "Lịch hẹn này đã được hủy trước đó."

        df.loc[mask, 'status'] = 'Đã hủy'
        if CSVHelper.save_appointments(df):
            return True, "Hủy lịch hẹn thành công."
        return False, "Lỗi hệ thống khi cập nhật lịch hẹn."

    @classmethod
    def confirm_payment(cls, appointment_id: str, user_id: str) -> Tuple[bool, str]:
        """Confirm payment for an existing booking, changing its status."""
        df = CSVHelper.get_appointments()
        if df.empty:
            return False, "Không tìm thấy dữ liệu lịch hẹn."

        mask = (df['id'] == appointment_id) & (df['user_id'] == user_id)
        if not mask.any():
            return False, "Lịch hẹn không tồn tại hoặc không thuộc quyền sở hữu của bạn."

        current_status = df.loc[mask, 'status'].values[0].strip()
        if current_status == 'Đã hủy':
            return False, "Không thể thanh toán cho lịch hẹn đã hủy."
        elif current_status == 'Đã thanh toán':
            return False, "Lịch hẹn này đã được thanh toán rồi."

        df.loc[mask, 'status'] = 'Đã thanh toán'
        if CSVHelper.save_appointments(df):
            return True, "Xác nhận thanh toán thành công. Cảm ơn bạn!"
        return False, "Lỗi hệ thống khi cập nhật lịch hẹn."

    @classmethod
    def update_booking_time(cls, appointment_id: str, user_id: str, new_date: str, new_time: str) -> Tuple[bool, str]:
        """Update date/time of a booking (reschedule).
        
        Uses _booking_lock to prevent two concurrent reschedules from both
        grabbing the same slot at the same time.
        """
        # BUG FIX #2: Validate that the new date/time is not in the past
        try:
            new_date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
            if new_date_obj < datetime.today().date():
                return False, "Không thể đổi lịch sang ngày đã qua."
            if new_date_obj == datetime.today().date() and new_time <= datetime.now().strftime('%H:%M'):
                return False, "Không thể đổi lịch sang khung giờ đã qua trong ngày hôm nay."
            if new_time not in cls.STANDARD_SLOTS:
                return False, "Khung giờ khám không hợp lệ."
        except ValueError:
            return False, "Định dạng ngày không hợp lệ (hãy dùng YYYY-MM-DD)."

        # ──── CRITICAL SECTION ────
        with cls._booking_lock:
            df = CSVHelper.get_appointments()
            if df.empty:
                return False, "Không tìm thấy dữ liệu lịch hẹn."

            mask = (df['id'] == appointment_id) & (df['user_id'] == user_id)
            if not mask.any():
                return False, "Lịch hẹn không tồn tại."

            current_status = df.loc[mask, 'status'].values[0].strip()
            if current_status == 'Đã hủy':
                return False, "Không thể đổi lịch cho lịch hẹn đã hủy."

            doctor_id = df.loc[mask, 'doctor_id'].values[0]

            # Check collision for new slot (excluding current appointment itself)
            df_others = df[df['id'] != appointment_id]
            active_others = df_others[
                (df_others['doctor_id'] == doctor_id) & 
                (df_others['date'] == new_date) &
                (df_others['status'].str.strip() != 'Đã hủy')
            ]
            
            if new_time in active_others['time'].tolist():
                booked_slots = cls.get_doctor_appointments_on_date(doctor_id, new_date)
                if df.loc[mask, 'date'].values[0] == new_date:
                    current_time = df.loc[mask, 'time'].values[0]
                    if current_time in booked_slots:
                        booked_slots.remove(current_time)
                
                available_slots = cls._available_slots(booked_slots, new_date, limit=3)
                alt_str = ", ".join(available_slots)
                return False, f"Bác sĩ đã bận vào khung giờ mới này. Gợi ý giờ trống: {alt_str}."

            # Check user collision — người dùng đã có lịch khám cùng giờ với bác sĩ khác (loại trừ lịch hiện tại)
            if cls.check_user_collision(user_id, new_date, new_time, exclude_appointment_id=appointment_id):
                return False, f"Bạn đã có lịch khám vào {new_time} ngày {new_date} với một bác sĩ khác. Vui lòng chọn khung giờ khác."

            df.loc[mask, 'date'] = new_date
            df.loc[mask, 'time'] = new_time

            if CSVHelper.save_appointments(df):
                return True, "Đổi lịch hẹn thành công."
            return False, "Lỗi hệ thống khi cập nhật lịch hẹn."

