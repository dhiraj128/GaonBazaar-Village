import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_razorpay_order_and_verify_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Login as customer
        login_res = await client.post("/api/v1/auth/otp/send", json={"phone": "9800000000", "role": "customer"})
        assert login_res.status_code == 200
        session_id = login_res.json()["session_id"]
        
        verify_res = await client.post("/api/v1/auth/otp/verify", json={
            "phone": "9800000000",
            "otp": "123456",
            "session_id": session_id
        })
        assert verify_res.status_code == 200
        token = verify_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get customer addresses
        addr_res = await client.get("/api/v1/addresses", headers=headers)
        assert addr_res.status_code == 200
        addr_id = addr_res.json()[0]["id"]
        
        # 3. Get store products
        prod_res = await client.get("/api/v1/stores/str_01/products")
        assert prod_res.status_code == 200
        products = prod_res.json()
        assert len(products) > 0
        prod_id = products[0]["id"]
        
        # 4. Create Order with ONLINE payment method
        order_res = await client.post("/api/v1/orders", headers=headers, json={
            "store_id": "str_01",
            "delivery_address_id": addr_id,
            "payment_method": "ONLINE",
            "items": [{"product_id": prod_id, "quantity": 1}]
        })
        assert order_res.status_code == 201
        order_data = order_res.json()
        order_id = order_data["id"]
        assert order_data["payment_status"] in ["PENDING", "SIMULATED"]
        
        # 5. Create Razorpay Order
        rzp_order_res = await client.post("/api/v1/payments/razorpay/order", headers=headers, json={
            "order_id": order_id
        })
        assert rzp_order_res.status_code == 200
        rzp_order_data = rzp_order_res.json()
        assert rzp_order_data["id"].startswith("order_rzp_")
        assert rzp_order_data["currency"] == "INR"
        assert rzp_order_data["amount"] > 0
        
        # 6. Verify Razorpay Payment (Test mode mock signature)
        rzp_verify_res = await client.post("/api/v1/payments/razorpay/verify", headers=headers, json={
            "order_id": order_id,
            "razorpay_order_id": rzp_order_data["id"],
            "razorpay_payment_id": "pay_test_1234567890",
            "razorpay_signature": "test_sig_verified"
        })
        assert rzp_verify_res.status_code == 200
        verify_data = rzp_verify_res.json()
        assert verify_data["status"] == "SUCCESS"
        assert verify_data["payment_id"] == "pay_test_1234567890"
        
        # 7. Check order status now reflects PAID
        check_order = await client.get(f"/api/v1/orders/{order_id}", headers=headers)
        assert check_order.status_code == 200
        assert check_order.json()["payment_status"] == "PAID"
        assert check_order.json()["payment_method"] == "ONLINE"
