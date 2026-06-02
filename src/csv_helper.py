import os
import pandas as pd
from config import Config

class CSVHelper:
    _cache = {}

    @classmethod
    def read_csv(cls, file_path):
        """Read a CSV file and return a pandas DataFrame, with caching based on file modification time. If file doesn't exist, return empty DataFrame."""
        if not os.path.exists(file_path):
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            return pd.DataFrame()
        try:
            mtime = os.path.getmtime(file_path)
            # Check cache
            if file_path in cls._cache:
                cached_mtime, cached_df = cls._cache[file_path]
                if cached_mtime == mtime:
                    return cached_df.copy() # Return a copy to prevent accidental mutation of the cache

            df = pd.read_csv(file_path, dtype=str)
            # Strip whitespace from all string columns to prevent key mismatches
            for col in df.select_dtypes(include='object').columns:
                df[col] = df[col].str.strip()
            
            # Update cache
            cls._cache[file_path] = (mtime, df)
            return df.copy()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return pd.DataFrame()

    @staticmethod
    def write_csv(df, file_path):
        """Write a pandas DataFrame to a CSV file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            df.to_csv(file_path, index=False)
            CSVHelper._cache.pop(file_path, None)
            return True
        except Exception as e:
            print(f"Error writing to {file_path}: {e}")
            return False

    @classmethod
    def get_users(cls):
        return cls.read_csv(Config.USERS_CSV)

    @classmethod
    def save_users(cls, df):
        return cls.write_csv(df, Config.USERS_CSV)

    @classmethod
    def get_clinics(cls):
        return cls.read_csv(Config.CLINICS_CSV)

    @classmethod
    def save_clinics(cls, df):
        return cls.write_csv(df, Config.CLINICS_CSV)

    @classmethod
    def get_doctors(cls):
        return cls.read_csv(Config.DOCTORS_CSV)

    @classmethod
    def save_doctors(cls, df):
        return cls.write_csv(df, Config.DOCTORS_CSV)

    @classmethod
    def get_appointments(cls):
        return cls.read_csv(Config.APPOINTMENTS_CSV)

    @classmethod
    def save_appointments(cls, df):
        return cls.write_csv(df, Config.APPOINTMENTS_CSV)

    @staticmethod
    def get_diseases():
        import json
        file_path = os.path.join(Config.DATA_DIR, 'diseases.json')
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []

    @staticmethod
    def get_doctors_info():
        import json
        file_path = os.path.join(Config.DATA_DIR, 'doctors_info.json')
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {}
