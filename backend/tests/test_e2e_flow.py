import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_full_order_and_delivery_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Customer login
        cust_login = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9876543210",
            "otp": "123456",
            "role": "customer"
        })
        assert cust_login.status_code == 200
        cust_token = cust_login.json()["access_token"]
        cust_headers = {"Authorization": f"Bearer {cust_token}"}
        
        # 2. Get customer saved addresses
        addr_resp = await client.get("/api/v1/addresses", headers=cust_headers)
        assert addr_resp.status_code == 200
        addresses = addr_resp.json()
        assert len(addresses) > 0
        address_id = addresses[0]["id"]
        
        # 3. Get nearby stores
        stores_resp = await client.get(
            f"/api/v1/stores/nearby?latitude={addresses[0]['latitude']}&longitude={addresses[0]['longitude']}"
        )
        assert stores_resp.status_code == 200
        stores = stores_resp.json()
        assert len(stores) >= 2
        store_id = stores[0]["id"]
        
        # 4. Get store products
        prods_resp = await client.get(f"/api/v1/stores/{store_id}/products")
        assert prods_resp.status_code == 200
        prods = prods_resp.json()
        assert len(prods) > 0
        product_id = prods[0]["id"]
        
        # 5. Sync cart
        cart_sync = await client.post("/api/v1/cart/sync", json={
            "store_id": store_id,
            "delivery_latitude": addresses[0]["latitude"],
            "delivery_longitude": addresses[0]["longitude"],
            "items": [{"product_id": product_id, "quantity": 2}]
        })
        assert cart_sync.status_code == 200
        cart_data = cart_sync.json()
        assert cart_data["platform_fee"] == 3.0
        assert cart_data["is_serviceable"] is True
        
        # 6. Place order
        order_create = await client.post("/api/v1/orders", headers=cust_headers, json={
            "store_id": store_id,
            "delivery_address_id": address_id,
            "payment_method": "COD",
            "items": [{"product_id": product_id, "quantity": 2}],
            "customer_notes": "Please call near Shiv Mandir"
        })
        assert order_create.status_code == 201
        order = order_create.json()
        order_id = order["id"]
        delivery_otp = order["delivery_otp"]
        assert order["status"] == "PLACED"
        assert order["platform_fee"] == 3.0
        assert order["can_cancel"] is True
        assert order["cancel_seconds_remaining"] > 170 # Within 180s window
        
        # 7. Vendor login & accepts order
        vendor_login = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9800000001",
            "otp": "123456",
            "role": "vendor"
        })
        v_token = vendor_login.json()["access_token"]
        v_headers = {"Authorization": f"Bearer {v_token}"}
        
        v_accept = await client.post(
            f"/api/v1/vendor/orders/{order_id}/action",
            headers=v_headers,
            json={"action": "ACCEPT"}
        )
        assert v_accept.status_code == 200
        
        # Vendor packs order
        v_pack = await client.post(
            f"/api/v1/vendor/orders/{order_id}/action",
            headers=v_headers,
            json={"action": "PACKED"}
        )
        assert v_pack.status_code == 200
        
        # 8. Runner login & accepts job
        runner_login = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9800000003",
            "otp": "123456",
            "role": "runner"
        })
        r_token = runner_login.json()["access_token"]
        r_headers = {"Authorization": f"Bearer {r_token}"}
        
        r_accept = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=r_headers,
            json={"action": "ACCEPT"}
        )
        assert r_accept.status_code == 200
        
        # Runner picks up order
        r_pickup = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=r_headers,
            json={"action": "PICKUP"}
        )
        assert r_pickup.status_code == 200
        
        # Runner tests invalid OTP delivery -> should fail with 400
        r_bad_otp = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=r_headers,
            json={"action": "DELIVER", "delivery_otp": "0000"}
        )
        assert r_bad_otp.status_code == 400
        
        # Runner delivers with correct OTP -> completes delivery
        r_deliver = await client.post(
            f"/api/v1/runner/jobs/{order_id}/action",
            headers=r_headers,
            json={"action": "DELIVER", "delivery_otp": delivery_otp}
        )
        assert r_deliver.status_code == 200
        
        # 9. Verify order status is DELIVERED
        final_order = await client.get(f"/api/v1/orders/{order_id}", headers=cust_headers)
        assert final_order.status_code == 200
        final_data = final_order.json()
        assert final_data["status"] == "DELIVERED"
        assert final_data["payment_status"] == "PAID"
        assert len(final_data["timeline"]) >= 5
