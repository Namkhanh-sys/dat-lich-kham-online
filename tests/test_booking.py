import pytest
from datetime import datetime, timedelta
from src.booking_manager import BookingManager
from src.csv_helper import CSVHelper

TODAY = datetime.today()
TOMORROW_STR = (TODAY + timedelta(days=1)).strftime('%Y-%m-%d')
NEXT_DAY_STR = (TODAY + timedelta(days=2)).strftime('%Y-%m-%d')
FUTURE_DATE_STR = (TODAY + timedelta(days=30)).strftime('%Y-%m-%d')
FUTURE_DATE_STR_2 = (TODAY + timedelta(days=40)).strftime('%Y-%m-%d')
FUTURE_DATE_STR_3 = (TODAY + timedelta(days=60)).strftime('%Y-%m-%d')

def test_check_collision():
    # Doctor d1 is booked at 09:00 on tomorrow (created in conftest)
    collision = BookingManager.check_collision('d1', TOMORROW_STR, '09:00')
    assert collision is True

    # Doctor d1 is free at 10:00 on tomorrow
    no_collision = BookingManager.check_collision('d1', TOMORROW_STR, '10:00')
    assert no_collision is False

def test_suggest_alternative_slots():
    # Get standard slots but filter out the occupied '09:00' on tomorrow
    alternatives = BookingManager.suggest_alternative_slots('d1', TOMORROW_STR)
    assert len(alternatives) > 0
    assert '09:00' not in alternatives
    assert alternatives[0] == '08:00'

def test_create_booking():
    # Create booking for d1 at free slot on tomorrow
    success, app_dict = BookingManager.create_booking('u1', 'd1', TOMORROW_STR, '10:00')
    assert success is True
    assert app_dict['doctor_id'] == 'd1'
    assert app_dict['time'] == '10:00'

    # Try creating booking on a collision slot (09:00)
    success_col, msg = BookingManager.create_booking('u1', 'd1', TOMORROW_STR, '09:00')
    assert success_col is False
    assert "bác sĩ đã có lịch hẹn" in msg.lower()

def test_get_user_appointments():
    # User u1 has appointments
    apps = BookingManager.get_user_appointments('u1')
    assert len(apps) >= 1
    # Check join fields are present
    assert 'doctor_name' in apps[0]
    assert 'clinic_name' in apps[0]
    assert 'clinic_address' in apps[0]

def test_cancel_booking():
    # Cancel an appointment
    df = CSVHelper.get_appointments()
    app_id = df.iloc[0]['id']
    user_id = df.iloc[0]['user_id']

    success, msg = BookingManager.cancel_booking(app_id, user_id)
    assert success is True

    # Verify cancelled status
    df_after = CSVHelper.get_appointments()
    status = df_after[df_after['id'] == app_id]['status'].values[0]
    assert status == 'Đã hủy'

def test_reschedule_booking():
    # Setup test app
    success, app_dict = BookingManager.create_booking('u1', 'd2', NEXT_DAY_STR, '14:00')
    assert success is True
    app_id = app_dict['id']

    # Book another slot to make it busy
    success_other, _ = BookingManager.create_booking('u1', 'd2', NEXT_DAY_STR, '15:00')
    assert success_other is True

    # Reschedule to free slot
    success_res, msg_res = BookingManager.update_booking_time(app_id, 'u1', NEXT_DAY_STR, '16:00')
    assert success_res is True

    # Reschedule to busy slot (collision)
    success_res_busy, msg_res_busy = BookingManager.update_booking_time(app_id, 'u1', NEXT_DAY_STR, '15:00')
    assert success_res_busy is False
    assert "bận vào khung giờ mới" in msg_res_busy


# ── New edge-case tests covering Bug Fixes #1, #2, #5, #6 ─────────────────

def test_create_booking_rejects_past_date():
    """Bug Fix #1 + general: cannot book on past date."""
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    success, msg = BookingManager.create_booking('u1', 'd1', yesterday, '09:00')
    assert success is False
    assert "ngày đã qua" in msg.lower()

def test_create_booking_rejects_past_time_today():
    """Bug Fix #1: cannot book a time slot that has already passed today."""
    today_str = datetime.today().strftime('%Y-%m-%d')
    now_minus = (datetime.now() - timedelta(minutes=30)).strftime('%H:%M')
    # Find a STANDARD_SLOTS entry <= now_minus so it is definitely in the past
    past_slot = next((s for s in reversed(BookingManager.STANDARD_SLOTS) if s <= now_minus), None)
    if past_slot is None:
        pytest.skip("No past slot found at this time of day (tests running before 08:30)")
    success, msg = BookingManager.create_booking('u1', 'd1', today_str, past_slot)
    assert success is False
    assert ("hôm nay" in msg.lower() or "đã qua" in msg.lower())

def test_update_booking_time_rejects_past_date():
    """Bug Fix #2: rescheduling to a past date must be rejected."""
    success, app_dict = BookingManager.create_booking('u1', 'd1', FUTURE_DATE_STR, '10:00')
    assert success is True
    app_id = app_dict['id']

    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    success_r, msg_r = BookingManager.update_booking_time(app_id, 'u1', yesterday, '10:00')
    assert success_r is False
    assert "đã qua" in msg_r.lower()

def test_cancel_already_cancelled_booking():
    """Bug Fix #5: cancelling an already-cancelled booking must return an error."""
    success, app_dict = BookingManager.create_booking('u1', 'd2', FUTURE_DATE_STR_2, '09:00')
    assert success is True
    app_id = app_dict['id']

    # First cancel — should succeed
    ok1, _ = BookingManager.cancel_booking(app_id, 'u1')
    assert ok1 is True

    # Second cancel on same booking — should fail
    ok2, msg2 = BookingManager.cancel_booking(app_id, 'u1')
    assert ok2 is False
    assert "đã được hủy" in msg2.lower()

def test_reschedule_cancelled_booking_rejected():
    """Cannot reschedule an appointment that has already been cancelled."""
    success, app_dict = BookingManager.create_booking('u1', 'd2', FUTURE_DATE_STR_3, '09:00')
    assert success is True
    app_id = app_dict['id']

    ok_cancel, _ = BookingManager.cancel_booking(app_id, 'u1')
    assert ok_cancel is True

    ok_res, msg_res = BookingManager.update_booking_time(app_id, 'u1', FUTURE_DATE_STR_3, '14:00')
    assert ok_res is False
    assert "đã hủy" in msg_res.lower()

from unittest.mock import patch

def test_suggest_alternative_slots_excludes_past_times_today():
    """Bug Fix #6: slots returned for today must all be in the future."""
    today_str = datetime.today().strftime('%Y-%m-%d')
    
    # Mock datetime so we pretend it is 12:15 today. 
    # This prevents the function from skipping to tomorrow if it's run late at night.
    class MockDatetime(datetime):
        @classmethod
        def now(cls):
            return cls(2026, 6, 1, 12, 15, 0)
        @classmethod
        def today(cls):
            # We want today() to match whatever today_str is parsed from real datetime
            return datetime.strptime(today_str, '%Y-%m-%d')

    with patch('src.booking_manager.datetime', MockDatetime):
        now_time = '12:15'
        alternatives = BookingManager.suggest_alternative_slots('d1', today_str)
        for slot in alternatives:
            assert slot > now_time, f"Slot {slot} should be in the future (now={now_time})"
