import pytest
import base64
import time
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import issue_and_verify_test_token

@pytest.mark.asyncio
async def test_evidence_upload_and_ticket_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        ts = int(time.time() * 100) % 100000000
        phone = f"94{ts:08d}"
        headers = await issue_and_verify_test_token(client, phone, "customer")

        # 1. Valid minimal 1x1 JPEG with magic bytes \xff\xd8\xff
        # Minimal valid JPEG binary
        fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"
        b64_data = base64.b64encode(fake_jpeg).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{b64_data}"

        upload_res = await client.post("/api/v1/support/upload-evidence", headers=headers, json={
            "data_url": data_url,
            "file_name": "damaged_pack.jpg"
        })
        assert upload_res.status_code == 200, upload_res.text
        upload_data = upload_res.json()
        assert "evidence_id" in upload_data
        assert upload_data["attachment_url"].startswith("/api/v1/support/evidence/")
        assert upload_data["content_type"] == "image/jpeg"

        # 2. Retrieve file through GET /api/v1/support/evidence/{filename}
        filename = upload_data["file_name"]
        get_res = await client.get(f"/api/v1/support/evidence/{filename}", headers=headers)
        assert get_res.status_code == 200
        assert get_res.content == fake_jpeg
        assert get_res.headers["content-type"] == "image/jpeg"

        # 3. Create ticket with the uploaded evidence
        ticket_res = await client.post("/api/v1/support/tickets", headers=headers, json={
            "category": "DAMAGED_ITEM",
            "subject": "Torn Atta Bag Delivered",
            "message": "The outer packaging was severely damaged upon delivery.",
            "affected_product_id": "p1",
            "attachment_url": upload_data["attachment_url"]
        })
        assert ticket_res.status_code == 201, ticket_res.text
        t_data = ticket_res.json()
        assert t_data["attachment_url"] == upload_data["attachment_url"]
        assert t_data["category"] == "DAMAGED_ITEM"
        assert t_data["status"] == "OPEN"

        # 4. Invalid magic bytes rejection test
        bad_payload = "data:image/jpeg;base64," + base64.b64encode(b"NOT_A_JPEG_FILE").decode('utf-8')
        bad_res = await client.post("/api/v1/support/upload-evidence", headers=headers, json={
            "data_url": bad_payload
        })
        assert bad_res.status_code == 400
        assert "JPEG signature" in bad_res.json()["detail"]
