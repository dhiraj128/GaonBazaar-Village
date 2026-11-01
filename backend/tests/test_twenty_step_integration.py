import time
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_twenty_step_integrated_journey():
    """
    Executes the exact 20-step lifecycle requested in Section 9 of the Master Instruction.
    """
    ts = int(time.time() * 100) % 100000000
    vendor_phone = f"98{ts:08d}"
    customer_phone = f"97{ts:08d}"
    runner_phone = f"96{ts:08d}"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # STEP 1: Register a test Vendor
        v_reg = await client.post("/api/v1/auth/otp/verify", json={
            "phone": vendor_phone,
            "otp": "123456",
            "role": "vendor"
        })
        assert v_reg.status_code == 200
        v_token = v_reg.json()["access_token"]
        v_headers = {"Authorization": f"Bearer {v_token}"}
        
        # Onboard Store
        store_onboard = await client.post("/api/v1/stores/onboard", headers=v_headers, json={
            "shop_name": "Test Kisan Kirana Store",
            "owner_name": "Ramesh Kisan",
            "category": "Grocery",
            "latitude": 26.2230,
            "longitude": 85.3520,
            "village": "Chaturshi / Chatursi",
            "landmark": "Near Primary School",
            "block": "Minapur Block",
            "district": "Muzaffarpur",
            "upi_id": "ramesh.kisan@upi",
            "banner_url": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=500"
        })
        assert store_onboard.status_code == 200
        store = store_onboard.json()
        store_id = store["id"]
        assert store["is_approved"] is False # Quarantined prior to Admin review
        
        # STEP 2: Approve Vendor through Admin
        v_approve = await client.post(f"/api/v1/admin/vendors/{store_id}/approve")
        assert v_approve.status_code == 200
        assert v_approve.json()["is_approved"] is True
        
        # STEP 3 & 4: Add a real catalog product, image, stock, and price
        catalog_res = await client.get("/api/v1/catalog/global")
        assert catalog_res.status_code == 200
        cat_items = catalog_res.json()
        assert len(cat_items) >= 9
        
        # Pick Tomato / Chakki Atta from catalog
        selected_cat = cat_items[0]
        prod_add = await client.post("/api/v1/vendor/products", headers=v_headers, json={
            "global_product_id": selected_cat["id"],
            "custom_name_en": "Premium Chakki Atta (Kisan Special)",
            "custom_name_hi": "प्रीमियम चक्की आटा",
            "category": "Grocery",
            "unit": "5 kg",
            "price": 210.0, # Vendor custom selling price
            "mrp": 240.0,
            "image_url": selected_cat["image_url"],
            "stock_quantity": 50,
            "in_stock": True
        })
        assert prod_add.status_code == 200
        product = prod_add.json()
        product_id = product["id"]
        assert product["price"] == 210.0
        assert product["stock_quantity"] == 50
        
        # STEP 5: Register a test Customer
        c_reg = await client.post("/api/v1/auth/otp/verify", json={
            "phone": customer_phone,
            "otp": "123456",
            "role": "customer"
        })
        assert c_reg.status_code == 200
        c_token = c_reg.json()["access_token"]
        c_headers = {"Authorization": f"Bearer {c_token}"}
        
        # STEP 6: Choose a real confirmed test address (within Minapur pilot block, 1.2 km from store)
        addr_add = await client.post("/api/v1/addresses", headers=c_headers, json={
            "title": "Home",
            "recipient_name": "Anita Devi",
            "phone": customer_phone,
            "village": "Chaturshi / Chatursi",
            "landmark": "Near Shiv Mandir",
            "block": "Minapur",
            "district": "Muzaffarpur",
            "state": "Bihar",
            "latitude": 26.2200,
            "longitude": 85.3480,
            "is_default": True
        })
        assert addr_add.status_code == 201
        addr = addr_add.json()
        address_id = addr["id"]
        
        # STEP 7: Add product to Cart
        cart_check = await client.post("/api/v1/cart/sync", json={
            "store_id": store_id,
            "delivery_latitude": addr["latitude"],
            "delivery_longitude": addr["longitude"],
            "items": [{"product_id": product_id, "quantity": 1}]
        })
        assert cart_check.status_code == 200
        cart_data = cart_check.json()
        assert cart_data["is_serviceable"] is True
        assert cart_data["platform_fee"] == 3.0
        assert cart_data["subtotal"] == 210.0
        
        # STEP 8: Place a test COD order
        order_res = await client.post("/api/v1/orders", headers=c_headers, json={
            "store_id": store_id,
            "delivery_address_id": address_id,
            "payment_method": "COD",
            "items": [{"product_id": product_id, "quantity": 1}],
            "customer_notes": "Please call when reaching Shiv Mandir"
        })
        assert order_res.status_code == 201
        order = order_res.json()
        order_id = order["id"]
        delivery_otp = order["delivery_otp"]
        assert order["status"] == "PLACED"
        assert order["platform_fee"] == 3.0
        assert order["total_amount"] == 210.0 + order["delivery_fee"] + 3.0
        
        # STEP 9: Verify Vendor receives the order
        v_orders = await client.get("/api/v1/vendor/orders", headers=v_headers)
        assert v_orders.status_code == 200
        active_ids = [o["id"] for o in v_orders.json()]
        assert order_id in active_ids
        
        # STEP 10: Vendor accepts and prepares it
        v_acc = await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v_headers, json={"action": "ACCEPT"})
        assert v_acc.status_code == 200
        assert v_acc.json()["status"] == "ACCEPTED"
        
        v_prep = await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v_headers, json={"action": "PACKED"})
        assert v_prep.status_code == 200
        assert v_prep.json()["status"] == "PACKED"
        
        # STEP 11: Register and approve a test Runner
        r_reg = await client.post("/api/v1/auth/otp/verify", json={
            "phone": runner_phone,
            "otp": "123456",
            "role": "runner"
        })
        assert r_reg.status_code == 200
        r_user_id = r_reg.json()["user"]["id"]
        r_token = r_reg.json()["access_token"]
        r_headers = {"Authorization": f"Bearer {r_token}"}
        
        # Fetch runner list to get Runner entity ID
        runners_res = await client.get("/api/v1/admin/runners")
        assert runners_res.status_code == 200
        runners_list = runners_res.json()
        matching_runners = [r for r in runners_list if r.get("user_id") == r_user_id]
        assert len(matching_runners) > 0
        runner_id = matching_runners[0]["id"]
        
        r_app = await client.post(f"/api/v1/admin/runners/{runner_id}/approve")
        assert r_app.status_code == 200
        assert r_app.json()["is_approved"] is True
        
        # STEP 12: Runner accepts the assignment
        r_acc = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={"action": "ACCEPT"})
        assert r_acc.status_code == 200
        assert r_acc.json()["status"] == "RUNNER_ASSIGNED"
        
        # STEP 13, 14, 15: Runner inspects order details & confirms pickup
        job_info = await client.get(f"/api/v1/orders/{order_id}", headers=r_headers)
        assert job_info.status_code == 200
        j_data = job_info.json()
        assert j_data["store_name"] == "Test Kisan Kirana Store"
        assert "Shiv Mandir" in j_data["delivery_address"]
        
        r_pick = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={"action": "OUT_FOR_DELIVERY"})
        assert r_pick.status_code == 200
        assert r_pick.json()["status"] == "OUT_FOR_DELIVERY"
        
        # STEP 16 & 17: Verify delivery OTP and complete delivery
        # Wrong OTP fails with 400
        bad_del = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={
            "action": "DELIVER",
            "delivery_otp": "0000"
        })
        assert bad_del.status_code == 400
        
        # Correct OTP succeeds
        good_del = await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=r_headers, json={
            "action": "DELIVER",
            "delivery_otp": delivery_otp
        })
        assert good_del.status_code == 200
        assert good_del.json()["status"] == "DELIVERED"
        
        # STEP 18: Verify Customer sees Delivered
        cust_order = await client.get(f"/api/v1/orders/{order_id}", headers=c_headers)
        assert cust_order.status_code == 200
        c_data = cust_order.json()
        assert c_data["status"] == "DELIVERED"
        assert c_data["payment_status"] == "PAID"
        
        # STEP 19 & 20: Verify Admin order records and settlement calculations
        admin_orders = await client.get("/api/v1/admin/orders")
        assert admin_orders.status_code == 200
        admin_o_ids = [o["id"] for o in admin_orders.json()]
        assert order_id in admin_o_ids
        
        settlements = await client.get("/api/v1/admin/settlements")
        assert settlements.status_code == 200
        settle_data = settlements.json()
        assert settle_data["platform_fee_collected"] >= 3.0
        assert settle_data["vendor_payouts_due"] >= 210.0
