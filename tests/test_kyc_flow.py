import sys
import unittest
sys.path.insert(0, 'backend')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestKYCFlow(unittest.TestCase):
    def test_pan_verification_valid(self):
        resp = client.post("/api/v1/kyc/pan", json={
            "pan": "ABCDE1234F",
            "name": "Ramesh Kumar",
            "user_id": "test_user_kyc_1"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["valid"])
        self.assertEqual(data["status"], "VALID")
        self.assertEqual(data["pan"], "ABCDE1234F")
        self.assertEqual(data["kyc_status"], "pan_verified")
        self.assertIn("RAMESH", data["registered_name"])

    def test_pan_verification_invalid_format(self):
        resp = client.post("/api/v1/kyc/pan", json={
            "pan": "INVALID123",
            "name": "Ramesh Kumar"
        })
        self.assertEqual(resp.status_code, 400)

    def test_aadhaar_otp_dispatch(self):
        resp = client.post("/api/v1/kyc/aadhaar/otp", json={
            "aadhaar_number": "987654321098",
            "user_id": "test_user_kyc_1"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "SUCCESS")
        self.assertTrue(len(data["ref_id"]) > 0)

    def test_aadhaar_otp_verify(self):
        resp = client.post("/api/v1/kyc/aadhaar/verify", json={
            "otp": "123456",
            "ref_id": "cf_ref_test_123",
            "aadhaar_number": "987654321098",
            "user_id": "test_user_kyc_1"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "VALID")
        self.assertEqual(data["kyc_status"], "verified")
        self.assertTrue("kyc_photo_url" in data)
        self.assertIn("Chaturshi", data["address"])

if __name__ == '__main__':
    unittest.main()
