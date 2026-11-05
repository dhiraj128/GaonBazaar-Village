import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json

base = 'https://gaonbazaar-village.onrender.com'

def get_token(phone, role):
    s_req = urllib.request.Request(
        f"{base}/api/v1/auth/otp/send",
        data=json.dumps({"phone": phone, "role": role}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(s_req, timeout=15) as r:
        sess_id = json.loads(r.read().decode())["session_id"]
    
    v_req = urllib.request.Request(
        f"{base}/api/v1/auth/otp/verify",
        data=json.dumps({"phone": phone, "otp": "1234", "session_id": sess_id, "role": role}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(v_req, timeout=15) as r:
        return json.loads(r.read().decode())["access_token"]

token = get_token("9800000000", "customer")
o_req = urllib.request.Request(f'{base}/api/v1/orders', headers={'Authorization': f'Bearer {token}', 'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(o_req) as orr:
    orders = json.loads(orr.read().decode())
    print('Orders retrieved from Render backend for customer 9800000000:', len(orders))
    for o in orders:
        print(f"  - Order {o['id']}: Status={o['status']}, Total=₹{o.get('total_amount')}, Placed={o.get('placed_at')}")

# Also check admin orders
adm_token = get_token("9800000099", "admin")
all_orders_req = urllib.request.Request(f'{base}/api/v1/admin/orders/live', headers={'Authorization': f'Bearer {adm_token}', 'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(all_orders_req) as ar:
    all_orders = json.loads(ar.read().decode())
    print('\nTotal Live Orders in Admin feed:', len(all_orders))
    for o in all_orders:
        print(f"  - Admin Feed Order {o['id']}: Status={o['status']}, Customer={o.get('customer_name')}")
