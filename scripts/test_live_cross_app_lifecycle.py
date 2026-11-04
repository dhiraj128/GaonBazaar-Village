import sys
sys.stdout.reconfigure(encoding='utf-8')
import urllib.request
import json

base = "https://gaonbazaar-village.onrender.com"

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

def run_cross_app_live():
    print("=" * 60)
    print("GAONBAZAAR: CROSS-APP ORDER LIFECYCLE TEST ON LIVE RENDER")
    print("=" * 60)

    # 1. Customer places order
    print("\n--- STEP 1: CUSTOMER ---")
    cust_token = get_token("9800000000", "customer")
    cust_hdrs = {"Authorization": f"Bearer {cust_token}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

    # Get address and product
    addrs_req = urllib.request.Request(f"{base}/api/v1/addresses", headers=cust_hdrs)
    with urllib.request.urlopen(addrs_req, timeout=15) as r:
        addr_id = json.loads(r.read().decode())[0]["id"]

    prods_req = urllib.request.Request(f"{base}/api/v1/stores/str_01/products", headers=cust_hdrs)
    with urllib.request.urlopen(prods_req, timeout=15) as r:
        prod = json.loads(r.read().decode())[0]

    o_payload = json.dumps({
        "store_id": "str_01",
        "delivery_address_id": addr_id,
        "payment_method": "COD",
        "items": [{"product_id": prod["id"], "quantity": 1}],
        "customer_notes": "Cross-app live test order"
    }).encode()
    o_req = urllib.request.Request(f"{base}/api/v1/orders", data=o_payload, headers=cust_hdrs)
    with urllib.request.urlopen(o_req, timeout=15) as r:
        order = json.loads(r.read().decode())
        order_id = order["id"]
        otp = order["delivery_otp"]
        print(f"Customer created Order: {order_id}, Status: {order['status']}, OTP: {otp}")

    # 2. Vendor accepts and packs order
    print("\n--- STEP 2: VENDOR ---")
    v_token = get_token("9800000001", "vendor")
    v_hdrs = {"Authorization": f"Bearer {v_token}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

    act_payload = json.dumps({"action": "ACCEPT"}).encode()
    req = urllib.request.Request(f"{base}/api/v1/vendor/orders/{order_id}/action", data=act_payload, headers=v_hdrs)
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.loads(r.read().decode())
        print(f"Vendor ACCEPT: {res.get('message') or res}")

    pack_payload = json.dumps({"action": "PACK"}).encode()
    req = urllib.request.Request(f"{base}/api/v1/vendor/orders/{order_id}/action", data=pack_payload, headers=v_hdrs)
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.loads(r.read().decode())
        print(f"Vendor PACK: {res.get('message') or res}")

    # 3. Runner accepts, picks up, and delivers
    print("\n--- STEP 3: RUNNER ---")
    r_token = get_token("9800000003", "runner")
    r_hdrs = {"Authorization": f"Bearer {r_token}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}

    # Runner accepts
    r_accept = json.dumps({"action": "ACCEPT"}).encode()
    req = urllib.request.Request(f"{base}/api/v1/runner/jobs/{order_id}/action", data=r_accept, headers=r_hdrs)
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"Runner ACCEPT: {json.loads(r.read().decode())}")

    # Runner picks up
    r_pick = json.dumps({"action": "PICKUP"}).encode()
    req = urllib.request.Request(f"{base}/api/v1/runner/jobs/{order_id}/action", data=r_pick, headers=r_hdrs)
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"Runner PICKUP: {json.loads(r.read().decode())}")

    # Runner out for delivery
    r_out = json.dumps({"action": "OUT_FOR_DELIVERY"}).encode()
    req = urllib.request.Request(f"{base}/api/v1/runner/jobs/{order_id}/action", data=r_out, headers=r_hdrs)
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"Runner OUT_FOR_DELIVERY: {json.loads(r.read().decode())}")

    # Runner tests wrong OTP -> 400
    r_bad = json.dumps({"action": "DELIVER", "delivery_otp": "0000", "cash_collected": True}).encode()
    req = urllib.request.Request(f"{base}/api/v1/runner/jobs/{order_id}/action", data=r_bad, headers=r_hdrs)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print("ERROR: Bad OTP should not succeed!")
    except urllib.error.HTTPError as e:
        print(f"Runner Bad OTP rejected as expected: {e.code} -> {e.read().decode()[:80]}")

    # Runner delivers with genuine OTP
    r_good = json.dumps({"action": "DELIVER", "delivery_otp": otp, "cash_collected": True}).encode()
    req = urllib.request.Request(f"{base}/api/v1/runner/jobs/{order_id}/action", data=r_good, headers=r_hdrs)
    with urllib.request.urlopen(req, timeout=15) as r:
        print(f"Runner DELIVER with genuine OTP: {json.loads(r.read().decode())}")

    # 4. Final verification as Customer
    print("\n--- STEP 4: VERIFY DELIVERED STATE ---")
    final_req = urllib.request.Request(f"{base}/api/v1/orders/{order_id}", headers=cust_hdrs)
    with urllib.request.urlopen(final_req, timeout=15) as r:
        final_order = json.loads(r.read().decode())
        print(f"Order Final Status: {final_order['status']}")
        print(f"Payment Status: {final_order['payment_status']}")
        print(f"Timeline entries: {len(final_order['timeline'])}")
        assert final_order["status"] == "DELIVERED"
        assert final_order["payment_status"] == "PAID"
        print("ALL REAL CROSS-APP LIFECYCLE CHECKS PASSED ON LIVE SUPABASE POSTGRESQL!")

    print("=" * 60)

if __name__ == "__main__":
    run_cross_app_live()
