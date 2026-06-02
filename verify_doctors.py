import pandas as pd

df_doctors = pd.read_csv('data/doctors.csv')
df_clinics = pd.read_csv('data/clinics.csv')

# Kiểm tra số bác sĩ per clinic
print("Bác sĩ per clinic:")
print(df_doctors['clinic_id'].value_counts().sort_index())

print("\n\nBác sĩ per clinic per specialty (sample c11):")
c11_doctors = df_doctors[df_doctors['clinic_id'] == 'c11']
print(c11_doctors['specialty'].value_counts())

print(f"\nTổng bác sĩ c11: {len(c11_doctors)}")
print(f"Tổng clinics: {len(df_clinics)}")
print(f"Tổng doctors: {len(df_doctors)}")
