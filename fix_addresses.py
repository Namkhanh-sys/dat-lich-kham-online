import csv

with open('data/clinics.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rows = list(reader)

fixed_count = 0
for i in range(1, len(rows)):
    row = rows[i]
    if len(row) > 5:
        addr = row[2]
        city = row[5]
        
        # Nếu ở Hà Nội mà lại ghi TP. HCM
        if city == 'Hà Nội' and ', TP. Hồ Chí Minh' in addr:
            row[2] = addr.replace(', TP. Hồ Chí Minh', ', Hà Nội')
            fixed_count += 1
            
        # Ngược lại, nếu ở TP. HCM mà lại ghi Hà Nội
        elif city == 'TP. Hồ Chí Minh' and ', Hà Nội' in addr:
            row[2] = addr.replace(', Hà Nội', ', TP. Hồ Chí Minh')
            fixed_count += 1

with open('data/clinics.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print(f"Đã sửa {fixed_count} địa chỉ bị sai lệch.")
