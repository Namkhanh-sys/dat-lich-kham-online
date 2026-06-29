-- ============================================================
-- init_db.sql — Khởi tạo schema cho Supabase PostgreSQL
-- Chạy lần đầu sau khi tạo project Supabase
-- SQL Editor: https://supabase.com/dashboard/project/<id>/sql
-- ============================================================

-- Bảng người dùng
CREATE TABLE IF NOT EXISTS users (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone       TEXT NOT NULL DEFAULT ''
);

-- Bảng phòng khám
CREATE TABLE IF NOT EXISTS clinics (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    address     TEXT NOT NULL DEFAULT '',
    lat         DOUBLE PRECISION DEFAULT 0,
    lon         DOUBLE PRECISION DEFAULT 0,
    district    TEXT DEFAULT '',
    city        TEXT DEFAULT ''
);

-- Bảng bác sĩ
CREATE TABLE IF NOT EXISTS doctors (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    specialty   TEXT DEFAULT '',
    symptoms    TEXT DEFAULT '',
    clinic_id   TEXT REFERENCES clinics(id) ON DELETE SET NULL
);

-- Bảng lịch hẹn
CREATE TABLE IF NOT EXISTS appointments (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    doctor_id   TEXT NOT NULL,
    date        TEXT NOT NULL,
    time        TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'Da xac nhan'
);

-- Index tăng tốc truy vấn phổ biến
CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments(user_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_date ON appointments(doctor_id, date);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Tài khoản mặc định (thay đổi password_hash nếu cần)
-- password_hash bên dưới tương ứng với mật khẩu gốc trong users.csv
INSERT INTO users (id, name, email, password_hash, phone)
VALUES (
    'u_575f8889',
    'Do Nam Khanh',
    'knamkanh@gmail.com',
    '6e32556bd2df96bb02816a6a0d3cdc0a50e2e1517018eb048912dd88c53f6488',
    '0354952306'
)
ON CONFLICT (id) DO NOTHING;
