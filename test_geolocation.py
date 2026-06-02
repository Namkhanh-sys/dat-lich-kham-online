#!/usr/bin/env python
from app import app
import json

client = app.test_client()
resp = client.get('/api/geolocation/by-ip')
print('Status:', resp.status_code)
data = resp.get_json()
print(json.dumps(data, indent=2))
