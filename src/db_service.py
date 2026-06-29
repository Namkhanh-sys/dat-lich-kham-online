"""
DatabaseService — Thay thế CSVHelper khi DATABASE_URL được cấu hình.

Kết nối Supabase (PostgreSQL) qua psycopg2, giữ nguyên interface
trả về pd.DataFrame giống CSVHelper để không cần sửa code nghiệp vụ.

Được tự động chọn bởi CSVHelper nếu DATABASE_URL có trong env.
"""
from __future__ import annotations

import threading
from typing import Any
import pandas as pd

try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


class DatabaseService:
    """PostgreSQL-backed persistence layer for Supabase."""

    _lock = threading.RLock()
    _conn = None          # Shared connection (re-created if closed)
    _db_url: str = ""

    # ── Column definitions ──────────────────────────────────────────────────
    USER_COLS        = ['id', 'name', 'email', 'password_hash', 'phone']
    CLINIC_COLS      = ['id', 'name', 'address', 'lat', 'lon', 'district', 'city']
    DOCTOR_COLS      = ['id', 'name', 'specialty', 'symptoms', 'clinic_id']
    APPOINTMENT_COLS = ['id', 'user_id', 'doctor_id', 'date', 'time', 'status']

    @classmethod
    def init(cls, database_url: str) -> None:
        cls._db_url = database_url

    @classmethod
    def _get_conn(cls):
        """Return a live psycopg2 connection, re-creating if needed."""
        if not HAS_PSYCOPG2:
            raise RuntimeError("psycopg2 not installed. Run: pip install psycopg2-binary")
        with cls._lock:
            try:
                if cls._conn is None or cls._conn.closed:
                    cls._conn = psycopg2.connect(cls._db_url, connect_timeout=10)
                    cls._conn.autocommit = False
            except Exception as e:
                cls._conn = None
                raise RuntimeError(f"[DB] Cannot connect to database: {e}") from e
            return cls._conn

    # ── Generic helpers ─────────────────────────────────────────────────────

    @classmethod
    def _fetch(cls, sql: str, params=()) -> pd.DataFrame:
        """Execute SELECT and return DataFrame."""
        try:
            conn = cls._get_conn()
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame([dict(r) for r in rows]).fillna('').astype(str)
        except Exception as e:
            print(f"[DB] Fetch error: {e}")
            with cls._lock:
                cls._conn = None   # Force reconnect next time
            return pd.DataFrame()

    @classmethod
    def _upsert_table(cls, table: str, df: pd.DataFrame, pk: str = 'id') -> bool:
        """
        Sync a DataFrame to a PostgreSQL table using upsert.

        Strategy: DELETE rows not in df, then INSERT OR UPDATE all rows in df.
        This matches the CSV 'overwrite' pattern used by CSVHelper.
        """
        if df.empty:
            return True
        try:
            conn = cls._get_conn()
            with conn.cursor() as cur:
                cols   = list(df.columns)
                ids    = df[pk].tolist()

                # Remove rows deleted from DataFrame
                cur.execute(
                    f"DELETE FROM {table} WHERE {pk} NOT IN %s",
                    (tuple(ids) if len(ids) > 1 else (ids[0], ids[0]),)
                )

                # Upsert each row
                placeholders = ', '.join(['%s'] * len(cols))
                col_list     = ', '.join(cols)
                update_set   = ', '.join(
                    f"{c} = EXCLUDED.{c}" for c in cols if c != pk
                )
                sql = (
                    f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
                    f"ON CONFLICT ({pk}) DO UPDATE SET {update_set}"
                )
                for _, row in df.iterrows():
                    cur.execute(sql, [str(row[c]) if row[c] is not None else '' for c in cols])

            conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Upsert error on '{table}': {e}")
            with cls._lock:
                try:
                    cls._conn.rollback()
                except Exception:
                    cls._conn = None
            return False

    @classmethod
    def _insert_row(cls, table: str, row: dict, pk: str = 'id') -> bool:
        """Insert a single new row (used for append-only saves)."""
        try:
            conn = cls._get_conn()
            cols  = list(row.keys())
            vals  = [str(v) if v is not None else '' for v in row.values()]
            col_list     = ', '.join(cols)
            placeholders = ', '.join(['%s'] * len(cols))
            update_set   = ', '.join(
                f"{c} = EXCLUDED.{c}" for c in cols if c != pk
            )
            sql = (
                f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
                f"ON CONFLICT ({pk}) DO UPDATE SET {update_set}"
            )
            with conn.cursor() as cur:
                cur.execute(sql, vals)
            conn.commit()
            return True
        except Exception as e:
            print(f"[DB] Insert error on '{table}': {e}")
            with cls._lock:
                try:
                    cls._conn.rollback()
                except Exception:
                    cls._conn = None
            return False

    # ── Public API — mirrors CSVHelper ────────────────────────────────────

    @classmethod
    def get_users(cls) -> pd.DataFrame:
        df = cls._fetch("SELECT * FROM users ORDER BY id")
        if df.empty:
            return pd.DataFrame(columns=cls.USER_COLS)
        return df[cls.USER_COLS] if all(c in df.columns for c in cls.USER_COLS) else df

    @classmethod
    def save_users(cls, df: pd.DataFrame) -> bool:
        return cls._upsert_table('users', df[cls.USER_COLS] if not df.empty else df)

    @classmethod
    def get_clinics(cls) -> pd.DataFrame:
        df = cls._fetch("SELECT * FROM clinics ORDER BY id")
        if df.empty:
            return pd.DataFrame(columns=cls.CLINIC_COLS)
        return df[cls.CLINIC_COLS] if all(c in df.columns for c in cls.CLINIC_COLS) else df

    @classmethod
    def save_clinics(cls, df: pd.DataFrame) -> bool:
        return cls._upsert_table('clinics', df)

    @classmethod
    def get_doctors(cls) -> pd.DataFrame:
        df = cls._fetch("SELECT * FROM doctors ORDER BY id")
        if df.empty:
            return pd.DataFrame(columns=cls.DOCTOR_COLS)
        return df[cls.DOCTOR_COLS] if all(c in df.columns for c in cls.DOCTOR_COLS) else df

    @classmethod
    def save_doctors(cls, df: pd.DataFrame) -> bool:
        return cls._upsert_table('doctors', df)

    @classmethod
    def get_appointments(cls) -> pd.DataFrame:
        df = cls._fetch("SELECT * FROM appointments ORDER BY date, time")
        if df.empty:
            return pd.DataFrame(columns=cls.APPOINTMENT_COLS)
        return df[cls.APPOINTMENT_COLS] if all(c in df.columns for c in cls.APPOINTMENT_COLS) else df

    @classmethod
    def save_appointments(cls, df: pd.DataFrame) -> bool:
        return cls._upsert_table('appointments', df)

