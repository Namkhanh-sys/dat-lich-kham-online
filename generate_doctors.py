import pandas as pd
import random

print("🔄 Starting...")

# Đọc file cũ
df_old = pd.read_csv('data/doctors.csv')
print(f"✅ Bác sĩ cũ: {len(df_old)}")

# Danh sách quận
districts = {
    'Hà Nội': {
        'Hoàn Kiếm': (21.0278, 105.8523),
        'Ba Đình': (21.0362, 105.8340),
        'Cầu Giấy': (21.0366, 105.7820),
        'Hai Bà Trưng': (21.0115, 105.8505),
        'Thanh Xuân': (21.0035, 105.8484),
        'Đống Đa': (21.0200, 105.8500),
        'Tây Hồ': (21.0750, 105.8250),
        'Long Biên': (21.0750, 105.8850),
    },
    'TP. Hồ Chí Minh': {
        'Quận 1': (10.7769, 106.6956),
        'Quận 3': (10.7846, 106.6910),
        'Quận 5': (10.7600, 106.6730),
        'Quận 7': (10.7350, 106.7200),
        'Bình Thạnh': (10.8119, 106.7126),
        'Quận 11': (10.8300, 106.6600),
        'Phú Nhuận': (10.7950, 106.7350),
    },
    'Đà Nẵng': {
        'Hải Châu': (16.0600, 108.2050),
        'Thanh Khê': (16.0750, 108.1750),
        'Sơn Trà': (16.0900, 108.2300),
    }
}

# 8 specialty
specialties = {
    'Cơ xương khớp': 'thoát vị đĩa đệm;thoái hóa khớp;viêm khớp;đau lưng;đau khớp',
    'Tim mạch': 'cao huyết áp;rối loạn nhịp tim;xơ vữa;đau ngực;khó thở',
    'Hô hấp': 'hen suyễn;viêm phế quản;viêm xoang;khó thở;ho',
    'Tiêu hóa': 'đau bụng;buồn nôn;tiêu chảy;đau dạ dày;trào ngược',
    'Gan mật': 'gan nhiễm mỡ;viêm gan;xơ gan;vàng da;sỏi mật',
    'Nội tiết': 'tiểu đường;cường giáp;suy giáp;gout;béo phì',
    'Da liễu': 'viêm da;mề đay;mụn trứng cá;ngứa da;dị ứng',
    'Thần kinh': 'đau nửa đầu;mất ngủ;suy nhược;chóng mặt;tê bì',
}

# Tên Việt
first_names = ['Nguyễn', 'Trần', 'Phạm', 'Lê', 'Hoàng', 'Vũ', 'Ngô', 'Đỗ', 'Đinh', 'Dương', 'Bùi', 'Cao', 'Tô', 'Tạ']
middle_names = ['Văn', 'Thị', 'Quốc', 'Anh', 'Minh', 'Hùng', 'Phúc', 'Thanh', 'Hương', 'Linh', 'Đức', 'Long', 'Tuấn', 'Kiên']
last_names = ['Anh', 'Bình', 'Chương', 'Dũng', 'Giang', 'Hùng', 'Ích', 'Khánh', 'Linh', 'Minh', 'Nhật', 'Oanh', 'Phong', 'Thắng']
titles = ['TS. Dr.', 'PGS. TS.', 'Dr.', 'Bác sĩ', 'ThS. Dr.']

# Tạo clinics mới
df_clinics_old = pd.read_csv('data/clinics.csv')
clinics_new = []
clinic_id = 11

for city, city_districts in districts.items():
    for district, (lat, lon) in city_districts.items():
        clinic_name = f'Phòng khám Đa khoa {district}'
        clinics_new.append({
            'id': f'c{clinic_id}',
            'name': clinic_name,
            'address': f'{clinic_id} Đường {district} {city}',
            'lat': lat,
            'lon': lon,
            'city': city
        })
        clinic_id += 1

df_clinics_all = pd.concat([df_clinics_old, pd.DataFrame(clinics_new)], ignore_index=True)
df_clinics_all.to_csv('data/clinics.csv', index=False)
print(f"✅ Clinics: {len(df_clinics_all)}")

# Tạo bác sĩ mới
doctors_new = []
doc_id = 2000
clinic_id = 11

for city, city_districts in districts.items():
    for district, (lat, lon) in city_districts.items():
        for specialty, symptoms in specialties.items():
            for i in range(10):
                title = random.choice(titles)
                first = random.choice(first_names)
                middle = random.choice(middle_names)
                last = random.choice(last_names)
                name = f'{title} {first} {middle} {last}'
                
                doctors_new.append({
                    'id': f'd{doc_id}',
                    'name': name,
                    'specialty': specialty,
                    'symptoms': symptoms,
                    'clinic_id': f'c{clinic_id}'
                })
                doc_id += 1
        clinic_id += 1

df_new = pd.DataFrame(doctors_new)
print(f"📊 Bác sĩ mới created: {len(df_new)}")

df_doctors_all = pd.concat([df_old, df_new], ignore_index=True)
df_doctors_all.to_csv('data/doctors.csv', index=False)

print(f"✅ Bác sĩ mới: {len(df_new)}")
print(f"✅ Tổng bác sĩ: {len(df_doctors_all)}")
print("✅ DONE!")
