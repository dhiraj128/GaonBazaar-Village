import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json

def test_live_api():
    print("=" * 60)
    print("GAONBAZAAR: LIVE RENDER API INTEGRATION TEST")
    print("=" * 60)

    base = "https://gaonbazaar-village.onrender.com"
    
    # 1. Send OTP
    s_url = f"{base}/api/v1/auth/otp/send"
    s_data = json.dumps({"phone": "9800000000", "role": "customer"}).encode()
    s_req = urllib.request.Request(s_url, data=s_data, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(s_req, timeout=15) as sr:
        s_res = json.loads(sr.read().decode())
        sess_id = s_res["session_id"]
        print(f"[OTP SEND OK] Session: {sess_id}, Channel: {s_res.get('delivery_channel')}")

    # 2. Verify OTP
    v_url = f"{base}/api/v1/auth/otp/verify"
    v_data = json.dumps({"phone": "9800000000", "otp": "1234", "session_id": sess_id, "role": "customer"}).encode()
    v_req = urllib.request.Request(v_url, data=v_data, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(v_req, timeout=15) as vr:
        v_res = json.loads(vr.read().decode())
        token = v_res["access_token"]
        user = v_res["user"]
        print(f"[AUTH OK] User: {user['name']} ({user['phone']}), Role: {user['role']}")

    # 3. Get customer addresses
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0"}
    a_req = urllib.request.Request(f"{base}/api/v1/addresses", headers=headers)
    with urllib.request.urlopen(a_req, timeout=15) as ar:
        addrs = json.loads(ar.read().decode())
        print(f"[ADDRESSES OK] Retrieved {len(addrs)} saved addresses from Supabase PostgreSQL")
        for a in addrs[:2]:
            print(f"  - ID: {a['id']}, Village: {a['village']}, Landmark: {a.get('landmark')}")

    # 4. Get nearby stores and products
    s_req = urllib.request.Request(f"{base}/api/v1/stores/nearby?latitude=26.2315&longitude=85.3610", headers=headers)
    with urllib.request.urlopen(s_req, timeout=15) as sr:
        stores = json.loads(sr.read().decode())
        print(f"[STORES OK] Found {len(stores)} stores nearby")
        store = stores[0]
        print(f"  - Selected Store: {store['shop_name']} ({store['id']}) in {store['village']}")

    p_req = urllib.request.Request(f"{base}/api/v1/stores/{store['id']}/products", headers=headers)
    with urllib.request.urlopen(p_req, timeout=15) as pr:
        prods = json.loads(pr.read().decode())
        print(f"[PRODUCTS OK] Store has {len(prods)} products")
        prod = prods[0]
        print(f"  - Sample: {prod['name_en']}, Price: ₹{prod['price']}, In Stock: {prod['in_stock']}")

    # 5. Cart Sync
    c_data = json.dumps({
        "store_id": store["id"],
        "delivery_latitude": 26.2315,
        "delivery_longitude": 85.3610,
        "items": [{"product_id": prod["id"], "quantity": 1}]
    }).encode()
    c_req = urllib.request.Request(f"{base}/api/v1/cart/sync", data=c_data, headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(c_req, timeout=15) as cr:
        cart = json.loads(cr.read().decode())
        print(f"[CART SYNC OK] Subtotal: ₹{cart['subtotal']}, Platform Fee: ₹{cart['platform_fee']}, Total: ₹{cart['total_amount']}, Serviceable: {cart['is_serviceable']}")

    # 6. Create Live Order (COD Mode)
    o_data = json.dumps({
        "store_id": store["id"],
        "delivery_address_id": addrs[0]["id"] if addrs else None,
        "payment_method": "COD",
        "items": [{"product_id": prod["id"], "quantity": 1}],
        "customer_notes": "Live integration verification order"
    }).encode()
    o_req = urllib.request.Request(f"{base}/api/v1/orders", data=o_data, headers={"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(o_req, timeout=15) as orr:
            order = json.loads(orr.read().decode())
            print(f"[ORDER PLACED OK] Order ID: {order['id']}, Status: {order['status']}, OTP: {order['delivery_otp']}")
            
            # 7. Check Tracking endpoint
            tr_req = urllib.request.Request(f"{base}/api/v1/orders/{order['id']}/tracking", headers=headers)
            with urllib.request.urlopen(tr_req, timeout=15) as trr:
                track = json.loads(trr.read().decode())
                print(f"[TRACKING OK] Status: {track['status']}, Store: {track.get('store_name')}, Destination: {track.get('destination_village')}")
    except urllib.error.HTTPError as oe:
        print(f"[ORDER FAILED] {oe.code} -> {oe.read().decode()}")

    print("=" * 60)

if __name__ == "__main__":
    test_live_api()
