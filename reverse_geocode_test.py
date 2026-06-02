from app import app

with app.test_client() as client:
    response = client.get('/api/geocode/reverse?lat=21.0278&lon=105.8342')
    print('STATUS:', response.status_code)
    print(response.get_data(as_text=True))
