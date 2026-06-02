import hashlib
import uuid
import pandas as pd
from src.csv_helper import CSVHelper

class AuthService:
    @staticmethod
    def hash_password(password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @classmethod
    def register_user(cls, name, email, password, phone):
        """Register a new user. Returns (success, message)."""
        df = CSVHelper.get_users()
        
        # Check if email already exists
        if not df.empty and email.strip().lower() in df['email'].str.lower().values:
            return False, "Email này đã được đăng ký sử dụng."
        
        # Generate new unique user id
        user_id = f"u_{uuid.uuid4().hex[:8]}"
        password_hash = cls.hash_password(password)
        
        new_user = {
            'id': user_id,
            'name': name.strip(),
            'email': email.strip().lower(),
            'password_hash': password_hash,
            'phone': phone.strip()
        }
        
        # Append and save
        if df.empty:
            df = pd.DataFrame([new_user])
        else:
            df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
            
        if CSVHelper.save_users(df):
            return True, "Đăng ký thành công!"
        return False, "Lỗi hệ thống khi lưu thông tin người dùng."

    @classmethod
    def login_user(cls, email, password):
        """Verify user login credentials. Returns user dict or None."""
        df = CSVHelper.get_users()
        if df.empty:
            return None
            
        hashed_input = cls.hash_password(password)
        
        # Filter matching email and password hash
        user_row = df[(df['email'].str.lower() == email.strip().lower()) & (df['password_hash'] == hashed_input)]
        
        if not user_row.empty:
            return user_row.iloc[0].to_dict()
        return None

    @classmethod
    def update_profile(cls, user_id, name, phone):
        """Update user profile info. Returns (success, message)."""
        df = CSVHelper.get_users()
        if df.empty:
            return False, "Không tìm thấy thông tin người dùng."
            
        user_mask = df['id'] == user_id
        if not user_mask.any():
            return False, "Người dùng không tồn tại."
            
        df.loc[user_mask, 'name'] = name.strip()
        df.loc[user_mask, 'phone'] = phone.strip()
        
        if CSVHelper.save_users(df):
            return True, "Cập nhật thông tin thành công!"
        return False, "Lỗi lưu thông tin cập nhật."

    @classmethod
    def change_password(cls, user_id, old_password, new_password):
        """Change user password. Returns (success, message)."""
        df = CSVHelper.get_users()
        if df.empty:
            return False, "Không tìm thấy dữ liệu người dùng."
            
        user_mask = df['id'] == user_id
        if not user_mask.any():
            return False, "Người dùng không tồn tại."
            
        current_hash = df.loc[user_mask, 'password_hash'].values[0]
        if current_hash != cls.hash_password(old_password):
            return False, "Mật khẩu cũ không chính xác."
            
        df.loc[user_mask, 'password_hash'] = cls.hash_password(new_password)
        
        if CSVHelper.save_users(df):
            return True, "Đổi mật khẩu thành công!"
        return False, "Lỗi lưu mật khẩu mới."
