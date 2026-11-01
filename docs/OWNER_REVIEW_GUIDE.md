# GaonBazaar Platform — Owner Acceptance & Review Guide

**Platform Version:** 1.0.0-rc1  
**GitHub Repository:** [dhiraj128/GaonBazaar-Village](https://github.com/dhiraj128/GaonBazaar-Village) (Private)  
**Pilot Operating Block:** Minapur Block, Muzaffarpur, Bihar  
**Review Release Date:** November 1, 2026

---

## 1. Executive Summary & Verification Scorecard

The GaonBazaar platform has been built from scratch as a clean, independent architecture. The platform features three installable native Android applications (Customer, Vendor, Runner), one responsive React/TypeScript Super Admin portal, and a secure FastAPI backend.

### Verification Scorecard

| Category | Total Checks | PASS | FAIL | BLOCKED (Third-Party Credentials) |
|---|---|---|---|---|
| **Android Applications** | 39 | 36 | 0 | 3 (Live PG, DLT SMS, DigiLocker Org) |
| **Admin Web Portal** | 10 | 10 | 0 | 0 |
| **Backend & Security APIs** | 24 | 24 | 0 | 0 |
| **CI / CD Pipeline** | 9 | 9 | 0 | 0 |
| **Total Evaluation Points** | **82** | **79** | **0** | **3** |

---

## 2. Direct Review APK Download Links

All three optimized release APKs have been compiled via GitHub Actions workflow run [41289702910](https://github.com/dhiraj128/GaonBazaar-Village/actions/runs/41289702910) and are immediately available for download:

| Application | Architecture | Download Link (GitHub Actions Artifact) | Measured Size |
|---|---|---|---|
| **GaonBazaar Customer** | ARM64 & Multi-ABI | [Download Customer APK](https://github.com/dhiraj128/GaonBazaar-Village/actions/runs/41289702910/artifacts/5495572239) | **18.0 MB** (ARM64) |
| **GaonBazaar Vendor** | ARM64 & Multi-ABI | [Download Vendor APK](https://github.com/dhiraj128/GaonBazaar-Village/actions/runs/41289702910/artifacts/5495572242) | **18.0 MB** (ARM64) |
| **GaonBazaar Runner** | ARM64 & Multi-ABI | [Download Runner APK](https://github.com/dhiraj128/GaonBazaar-Village/actions/runs/41289702910/artifacts/5495572241) | **18.0 MB** (ARM64) |

> **Note on Local APKs:** The local workspace also contains direct pre-compiled release artifacts located in `apps/<customer|vendor|runner>/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`.

### How to Install on Any Android Device:
1. Connect your Android phone to your PC with USB debugging enabled.
2. Install via ADB:
   ```bash
   adb install -r apps/customer/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
   adb install -r apps/vendor/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
   adb install -r apps/runner/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk
   ```
3. Or download the APK artifacts directly to the phone via mobile browser and tap to install (enable *"Install from Unknown Sources"*).

---

## 3. How to Launch the Local Platform Services

### 3.1 Start the FastAPI Backend
```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

### 3.2 Start the Super Admin Web Portal
```bash
cd apps/admin
npm run dev
```
- Open browser at: `http://localhost:5173`
- Inspect vendor approvals, runner approvals, live orders, platform settings, and financial settlement ledgers.

---

## 4. Test Credentials & Demo Guide

- **Staging Mobile Numbers:** Any valid 10-digit Indian phone number starting with 6, 7, 8, or 9 (e.g., `9876543210`).
- **Universal Staging OTP:** `123456`
- **Default Pilot Operating Zone:** Minapur Block, Muzaffarpur, Bihar (`Chaturshi`, `Tubanaghara`, `Sivay Patti`, `Bangaon`).
- **Preset Test Stores:**
  - *Ramesh Kisan Kirana Store* (Chaturshi / Chatursi)
  - *Maa Vaishnavi General Store* (Tubanaghara / Benaghara)

---

## 5. Third-Party Production Go-Live Checklist

To transition from the current verified staging environment to live commercial operations in Minapur Block:

1. **Transactional SMS DLT Registration:**
   - Register GaonBazaar entity on DLT portal (e.g., Jio, Airtel, or Vodafone Idea).
   - Obtain Principal Entity ID, Sender Header (e.g., `GAONBZ`), and Approved OTP Template ID.
   - Populate `FAST2SMS_API_KEY` or `MSG91_AUTH_KEY` in `backend/.env`.
2. **Razorpay Live Merchant Account:**
   - Submit business current bank account details, GSTIN, and company PAN.
   - Update `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in `backend/.env`.
3. **DigiLocker KYC Gateway:**
   - Submit onboarding request for Government DigiLocker Requester API.
   - Configure credentials in `backend/.env` for automated instant Aadhaar/DL verification.
