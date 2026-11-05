import urllib.request
import re

for u in ['customer/', 'vendor/', 'runner/', 'admin/']:
    full = f'https://dhiraj128.github.io/GaonBazar-Village/{u}'
    try:
        req = urllib.request.Request(full, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode('utf-8', errors='ignore')
            title_match = re.search(r'<title>(.*?)</title>', body, re.IGNORECASE)
            title = title_match.group(1) if title_match else 'No Title'
            print(f"{u:10}: status={r.status}, length={len(body):6}, title='{title}'")
    except Exception as e:
        print(f"{u:10}: ERR {e}")
