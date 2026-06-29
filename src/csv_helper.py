import os
import json
import threading
from typing import Any, Dict, List, Optional, Union
import pandas as pd
from config import Config

# Import DatabaseService lazily to avoid hard dependency on psycopg2
_db_service = None

def _get_db():
    """Return initialized DatabaseService if DATABASE_URL is configured."""
    global _db_service
    if not Config.DATABASE_URL:
        return None
    if _db_service is None:
        try:
            from src.db_service import DatabaseService
            DatabaseService.init(Config.DATABASE_URL)
            _db_service = DatabaseService
            print(f"[CSVHelper] Using Supabase PostgreSQL for persistence.")
        except Exception as e:
            print(f"[CSVHelper] DB init failed, falling back to CSV: {e}")
            return None
    return _db_service


class CSVHelper:
    _cache: Dict[str, Dict[str, Any]] = {}
    _lock: threading.RLock = threading.RLock()

    @classmethod
    def read_csv(cls, file_path: str) -> pd.DataFrame:
        """Read a CSV file and return a DataFrame, reusing cache while the file is unchanged."""
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            return pd.DataFrame()
        try:
            stat = os.stat(file_path)
            cache_key = (stat.st_mtime_ns, stat.st_size)
            with cls._lock:
                cached = cls._cache.get(file_path)
                if cached and cached['key'] == cache_key:
                    return cached['data'].copy()

                df = pd.read_csv(file_path, dtype=str).fillna('')
                for col in df.columns:
                    if pd.api.types.is_string_dtype(df[col]):
                        df[col] = df[col].str.strip()
                cls._cache[file_path] = {'key': cache_key, 'data': df}
                return df.copy()
        except Exception as e:
            import traceback
            error_msg = f"[CSVHelper.read_csv] Error reading {file_path}: {e}\n{traceback.format_exc()}"
            print(error_msg)
            return pd.DataFrame()

    @staticmethod
    def write_csv(df: pd.DataFrame, file_path: str) -> bool:
        """Write a pandas DataFrame to a CSV file."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            temp_path = f"{file_path}.tmp"
            with CSVHelper._lock:
                df.to_csv(temp_path, index=False)
                os.replace(temp_path, file_path)
                CSVHelper._cache.pop(file_path, None)
            return True
        except Exception as e:
            import traceback
            error_msg = f"[CSVHelper.write_csv] Error writing to {file_path}: {e}\n{traceback.format_exc()}"
            print(error_msg)
            return False

    @classmethod
    def get_users(cls) -> pd.DataFrame:
        db = _get_db()
        if db:
            return db.get_users()
        return cls.read_csv(Config.USERS_CSV)

    @classmethod
    def save_users(cls, df: pd.DataFrame) -> bool:
        db = _get_db()
        if db:
            return db.save_users(df)
        return cls.write_csv(df, Config.USERS_CSV)


    @classmethod
    def get_clinics(cls) -> pd.DataFrame:
        return cls.read_csv(Config.CLINICS_CSV)

    @classmethod
    def save_clinics(cls, df: pd.DataFrame) -> bool:
        return cls.write_csv(df, Config.CLINICS_CSV)

    @classmethod
    def get_doctors(cls) -> pd.DataFrame:
        return cls.read_csv(Config.DOCTORS_CSV)

    @classmethod
    def save_doctors(cls, df: pd.DataFrame) -> bool:
        return cls.write_csv(df, Config.DOCTORS_CSV)

    @classmethod
    def get_appointments(cls) -> pd.DataFrame:
        db = _get_db()
        if db:
            return db.get_appointments()
        return cls.read_csv(Config.APPOINTMENTS_CSV)

    @classmethod
    def save_appointments(cls, df: pd.DataFrame) -> bool:
        db = _get_db()
        if db:
            return db.save_appointments(df)
        return cls.write_csv(df, Config.APPOINTMENTS_CSV)


    @staticmethod
    def get_diseases() -> List[Dict[str, Any]]:
        file_path = os.path.join(Config.DATA_DIR, 'diseases.json')
        if not os.path.exists(file_path):
            return []
        try:
            result = CSVHelper._read_json(file_path, [])
            if isinstance(result, list):
                return result
            return []
        except Exception as e:
            print(f"[ERROR] Error reading {file_path}: {e}")
            return []

    @staticmethod
    def get_doctors_info() -> Dict[str, Any]:
        file_path = os.path.join(Config.DATA_DIR, 'doctors_info.json')
        if not os.path.exists(file_path):
            return {}
        try:
            result = CSVHelper._read_json(file_path, {})
            if isinstance(result, dict):
                return result
            return {}
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return {}

    @staticmethod
    def _read_json(file_path: str, default: Any) -> Any:
        stat = os.stat(file_path)
        cache_key = (stat.st_mtime_ns, stat.st_size)
        with CSVHelper._lock:
            cached = CSVHelper._cache.get(file_path)
            if cached and cached['key'] == cache_key:
                return json.loads(json.dumps(cached['data']))

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            CSVHelper._cache[file_path] = {'key': cache_key, 'data': data}
            return json.loads(json.dumps(data))

