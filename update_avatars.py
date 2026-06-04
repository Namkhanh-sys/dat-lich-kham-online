import json
import random
import urllib.parse
from config import Config
import os

json_path = os.path.join(Config.DATA_DIR, 'doctors_info.json')

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

colors = ["2563eb", "059669", "dc2626", "d97706", "7c3aed", "db2777", "0284c7", "4f46e5"]

for doc_id, info in data.items():
    if doc_id == 'default':
        continue
        
    # Get first name from avatar URL or short_bio
    avatar_url = info.get('avatar', '')
    name = "BS"
    if 'name=' in avatar_url:
        import urllib.parse
        parsed = urllib.parse.urlparse(avatar_url)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'name' in qs:
            name = qs['name'][0]
    else:
        name = doc_id
        
    name_parts = name.strip().split()
    first_name = name_parts[-1] if name_parts else "BS"
    enc_name = urllib.parse.quote(first_name)
    
    color = random.choice(colors)
    info['avatar'] = f"https://ui-avatars.com/api/?name={enc_name}&background={color}&color=fff&size=200&length=1"

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Updated avatars successfully!")
