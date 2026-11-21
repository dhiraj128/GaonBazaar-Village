import pytest
import pytest_asyncio
import secrets
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_monthly_ration_list_lifecycle():
    transport = ASGITransport(app=app)
    uid = f"usr_test_{secrets.token_hex(4)}"
    phone = f"98{secrets.token_hex(4)}"[:10]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create token for unique customer
        token = create_access_token(data={"sub": uid, "phone": "9800000000", "role": "customer"})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. GET /api/v1/ration-lists (should auto-seed default list for new user)
        res = await client.get("/api/v1/ration-lists", headers=headers)
        assert res.status_code == 200, res.text
        data = res.json()
        assert len(data) >= 1
        first_list = data[0]
        assert first_list["name"] == "My Monthly Ration"
        assert len(first_list["items"]) >= 5
        list_id = first_list["id"]

        # Verify default items include staple flour, rice, oil
        names = [it["product_name_en"] for it in first_list["items"]]
        assert any("Atta" in n for n in names)
        assert any("Rice" in n for n in names)
        assert any("Oil" in n for n in names)

        # 2. PUT /api/v1/ration-lists/{id} (update list)
        update_payload = {
            "name": "Sharma Family Ration",
            "items": [
                {"product_id": "cat_atta", "product_name_en": "Chakki Fresh Atta", "product_name_hi": "चक्की आटा", "unit": "10 kg", "quantity": 1, "notes": "Double pack for festive month"},
                {"product_id": "cat_rice", "product_name_en": "Sonam Rice", "product_name_hi": "सोनम चावल", "unit": "10 kg", "quantity": 1, "notes": "10kg sack"},
                {"product_id": "cat_mustard_oil", "product_name_en": "Kachhi Ghani Mustard Oil", "product_name_hi": "सरसों तेल", "unit": "1 L", "quantity": 3, "notes": "3 bottles"}
            ]
        }
        u_res = await client.put(f"/api/v1/ration-lists/{list_id}", json=update_payload, headers=headers)
        assert u_res.status_code == 200
        u_data = u_res.json()
        assert u_data["name"] == "Sharma Family Ration"
        assert len(u_data["items"]) == 3

        # 3. POST /api/v1/ration-lists/{id}/validate-cart (check availability against stores)
        val_res = await client.post(f"/api/v1/ration-lists/{list_id}/validate-cart", headers=headers)
        assert val_res.status_code == 200
        val_data = val_res.json()
        assert val_data["list_id"] == list_id
        assert len(val_data["items"]) == 3
        assert val_data["total_estimated_amount"] > 0
        for item in val_data["items"]:
            assert "current_price" in item
            assert item["quantity"] >= 1

        # 4. User isolation test: Another customer should not see Sharma's list
        token2 = create_access_token(data={"sub": f"other_{uid}", "phone": "9876543210", "role": "customer"})
        res_other = await client.get(f"/api/v1/ration-lists/{list_id}", headers={"Authorization": f"Bearer {token2}"})
        assert res_other.status_code == 404

        # 5. Clean deletion
        del_res = await client.delete(f"/api/v1/ration-lists/{list_id}", headers=headers)
        assert del_res.status_code == 204

@pytest.mark.asyncio
async def test_address_management_api():
    transport = ASGITransport(app=app)
    uid = f"usr_addr_{secrets.token_hex(4)}"
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = create_access_token(data={"sub": uid, "phone": "9800000000", "role": "customer"})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create a new confirmed address
        addr_data = {
            "title": "Home",
            "recipient_name": "Ramesh Singh",
            "phone": "9800000000",
            "latitude": 26.2315,
            "longitude": 85.3610,
            "village": "Minapur",
            "landmark": "Near Panchayat Bhawan",
            "block": "Minapur",
            "district": "Muzaffarpur",
            "state": "Bihar",
            "is_default": True
        }
        c_res = await client.post("/api/v1/addresses", json=addr_data, headers=headers)
        assert c_res.status_code == 201
        created = c_res.json()
        addr_id = created["id"]
        assert created["village"] == "Minapur"
        assert created["is_default"] is True

        # 2. Update address (PUT)
        update_data = {
            "landmark": "Opposite Primary School & Mandir",
            "recipient_name": "Ramesh Kumar Singh"
        }
        u_res = await client.put(f"/api/v1/addresses/{addr_id}", json=update_data, headers=headers)
        assert u_res.status_code == 200
        updated = u_res.json()
        assert updated["landmark"] == "Opposite Primary School & Mandir"
        assert updated["recipient_name"] == "Ramesh Kumar Singh"

        # 3. Check serviceability against 8km rule
        serv_res = await client.post(
            "/api/v1/addresses/serviceability/check",
            json={"latitude": 26.2315, "longitude": 85.3610}
        )
        assert serv_res.status_code == 200
        serv_data = serv_res.json()
        assert serv_data["is_serviceable"] is True
        assert serv_data["distance_km"] <= 8.0

        # Beyond 8km check (Patna ~60km away)
        out_res = await client.post(
            "/api/v1/addresses/serviceability/check",
            json={"latitude": 25.5941, "longitude": 85.1376}
        )
        assert out_res.status_code == 200
        out_data = out_res.json()
        assert out_data["is_serviceable"] is False
        assert out_data["distance_km"] > 8.0
