# GaonBazaar Runner App — Complete Test & Verification Report

**Application Package:** `com.gaonbazaar.runner`  
**Platform Version:** Flutter 3.47.x / Dart 3.7.x  
**Target Operating Environment:** Android 8.0+ (API level 26+), Tested on Nothing Phone (2a) (Android 16 / SDK 36)  
**Measured Release APK Size:** 18.0 MB (`arm64-v8a`) / 50.7 MB (Universal)

---

## 1. Screen-by-Screen Navigation & Behavior Matrix

The Runner (Delivery Partner) App was tested across all navigable screens defined in `docs/SCREEN_REGISTRY.md`.

| Screen Name | File Path | Route | Visual Elements | Buttons & Actions Verified | Test Status |
|---|---|---|---|---|---|
| **Splash / Auth** | `lib/screens/runner_splash_screen.dart` | `/` | GaonBazaar Runner Logo, Loader | Checks token, redirects to Login or Dashboard | **PASS** |
| **Phone Login** | `lib/screens/runner_login_screen.dart` | `/login` | 10-digit textfield, +91 label, Send OTP | Validates runner mobile, submits OTP | **PASS** |
| **Verification Pending** | `lib/screens/runner_pending_screen.dart` | `/pending-verification` | Pending badge, KYC review info, support | Blocks order queue until Admin approves partner | **PASS** |
| **Runner Dashboard** | `lib/screens/runner_dashboard_screen.dart` | `/dashboard` | Online/Offline toggle, earnings summary, jobs | Broadcasts GPS, switches duty status | **PASS** |
| **Active Delivery Screen** | `lib/screens/runner_job_screen.dart` | `/active-job` | Pickup store info, drop village, map direction CTA | Direct phone dialer and GPS navigation links | **PASS** |
| **OTP Delivery Dialog** | `lib/screens/runner_job_screen.dart` | Modal | 4-digit PIN input, Confirm Delivery CTA | Validates OTP against backend; marks DELIVERED | **PASS** |
| **Earnings & History** | `lib/screens/runner_earnings_screen.dart` | `/earnings` | Daily trips, delivery fee earnings, payout status | Summarizes trip fees (₹15–₹35 tier payout) | **PASS** |

---

## 2. Key Business Logic & Delivery Safety Verifications

### 2.1 Partner Quarantine Prior to Super Admin KYC Approval
- **Requirement:** Section 5 requires delivery runners to be verified before they can view or accept customer delivery orders.
- **Verification:**
  - Runner registers with vehicle type (Motorcycle/Bicycle) and DL number.
  - Record created in database with `is_approved = False`.
  - Runner is gated at `runner_pending_screen.dart` with status: *"दस्तावेज़ सत्यापन प्रगति पर है (Verification Under Review)"*.
  - Runner is excluded from dispatch assignments until Super Admin approves via `/api/v1/admin/runners/{id}/approve`.

### 2.2 Live Job Acceptance & Dispatch State Machine
- **Requirement:** Real-time job claim preventing race conditions between multiple delivery runners.
- **Verification:**
  - When vendor marks order `PACKED`, job appears in available orders list for verified online runners.
  - Runner taps **स्वीकार करें (Accept Job)** -> calls `POST /api/v1/runner/jobs/{id}/action` with `{"action": "ACCEPT"}`.
  - Order state atomically updates to `RUNNER_ASSIGNED`, linking `runner_id` to the order.
  - Order is immediately removed from other runners' available queues.

### 2.3 Store Pickup & Route Navigation
- **Requirement:** Seamless transition from store pickup to customer doorstep navigation.
- **Verification:**
  - Upon reaching the store, runner taps **पिकअप पूरा हुआ (Order Picked Up)** -> status updates to `OUT_FOR_DELIVERY`.
  - App displays customer recipient name (`Anita Devi`), village (`Chaturshi`), and landmark (`Near Shiv Mandir`).
  - Tapping **कॉल करें (Call Customer)** triggers Android Intent `tel:+919700000000`.
  - Tapping **दिशा देखें (Open Map)** launches Google Maps navigation with exact village coordinates.

### 2.4 Mandatory 4-Digit Delivery OTP Handover
- **Requirement:** Section 5 & 8 strictly require delivery confirmation using the customer's 4-digit PIN to prevent misplacement or fraud.
- **Verification:**
  - Runner cannot complete the job without providing the OTP generated at order creation.
  - Test Step 16: Entering incorrect OTP (`0000`) returns HTTP 400 Bad Request: `"Invalid delivery OTP verification code"`.
  - Test Step 17: Entering customer's genuine OTP successfully transitions order to `DELIVERED`, records timestamp, marks COD payment as `PAID`, and credits runner delivery fee.

### 2.5 100% Delivery Fee Payout to Runner
- **Requirement:** Runner receives 100% of the customer delivery fee without platform deductions.
- **Verification:**
  - Tiered delivery fee (₹15 for <3km, ₹25 for 3-5km, ₹35 for 5-8km) is credited entirely to `runner_earnings_screen.dart`.
  - Admin settlement ledger explicitly validates runner payout matches total delivery fee collected.

---

## 3. Physical Device Testing & Stability

- **Test Device:** Nothing Phone (2a) (`A142`, Android 16)
- **Installation:** Clean installation using `adb install -r apps/runner/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`.
- **Battery & GPS Testing:** Background location ping throttled responsibly to prevent rural phone battery drain while maintaining accurate dispatch telemetry.
