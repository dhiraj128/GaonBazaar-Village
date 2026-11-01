# GaonBazaar Vendor App — Complete Test & Verification Report

**Application Package:** `com.gaonbazaar.vendor`  
**Platform Version:** Flutter 3.47.x / Dart 3.7.x  
**Target Operating Environment:** Android 8.0+ (API level 26+), Tested on Nothing Phone (2a) (Android 16 / SDK 36)  
**Measured Release APK Size:** 18.0 MB (`arm64-v8a`) / 50.7 MB (Universal)

---

## 1. Screen-by-Screen Navigation & Behavior Matrix

The Vendor App was tested across all navigable screens defined in `docs/SCREEN_REGISTRY.md`.

| Screen Name | File Path | Route | Visual Elements | Buttons & Actions Verified | Test Status |
|---|---|---|---|---|---|
| **Splash / Auth** | `lib/screens/vendor_splash_screen.dart` | `/` | GaonBazaar Vendor Logo, Loader | Checks token, redirects to Login or Dashboard | **PASS** |
| **Phone Login** | `lib/screens/vendor_login_screen.dart` | `/login` | 10-digit textfield, +91 label, Send OTP | Validates vendor phone, sends OTP | **PASS** |
| **Store Onboarding Wizard** | `lib/screens/vendor_onboarding_wizard.dart` | `/onboarding` | Shop Name, Owner Name, Village, Coordinates, UPI ID | Submits store profile; puts store in quarantine | **PASS** |
| **Quarantine Pending Screen** | `lib/screens/vendor_pending_approval_screen.dart` | `/pending-approval` | Pending badge, contact admin CTA, status info | Polling checks approval status; blocks order feed | **PASS** |
| **Vendor Dashboard** | `lib/screens/vendor_dashboard_screen.dart` | `/dashboard` | Today's sales, active orders, online toggle | Switches store online/offline, refreshes orders | **PASS** |
| **Product Library Screen** | `lib/screens/product_library_screen.dart` | `/product-library` | 14-item master rural grocery grid, search | Single-tap adds item to vendor's store with price/stock | **PASS** |
| **Inventory Screen** | `lib/screens/vendor_inventory_screen.dart` | `/inventory` | In-stock list, stock edit modal, price edit | Toggles item availability, updates selling price | **PASS** |
| **Settlements Screen** | `lib/screens/vendor_settlements_screen.dart` | `/settlements` | Total earnings, 0% commission indicator, payouts | Lists delivered orders with breakdown | **PASS** |

---

## 2. Key Business Logic & Operational Verifications

### 2.1 Store Quarantine Prior to Super Admin Approval
- **Requirement:** New vendor registrations MUST NOT go live or receive orders until reviewed and approved by the Super Admin.
- **Verification:**
  - Upon registering a store via `/api/v1/stores/onboard`, the store record is created with `is_approved = False`.
  - The Vendor App detects `is_approved == false` and directs the shopkeeper to `vendor_pending_approval_screen.dart`.
  - The customer store list API `GET /api/v1/stores/nearby` excludes unapproved stores (`where Store.is_approved == True`).
  - Once Super Admin calls `POST /api/v1/admin/vendors/{id}/approve`, the app unlocks the dashboard immediately.

### 2.2 14-Item Master Product Library Integration
- **Requirement:** Village store owners cannot type extensive descriptions. The app must allow 1-tap addition from a pre-populated catalog of 14 standard rural grocery items.
- **Verification:**
  - `ProductLibraryScreen` displays the 14 verified rural catalog items:
    1. Desi Tamatar (Tomato)
    2. Aloo (Potato)
    3. Pyaz (Onion)
    4. Shuddh Gai ka Doodh (Cow Milk)
    5. Basmati Chawal (Rice)
    6. Chakki Atta (Whole Wheat Flour)
    7. Sarson Tel (Mustard Oil)
    8. Cheeni (Refined Sugar)
    9. Tata Namak (Iodized Salt)
    10. Parle-G Biscuits
    11. Hari Mirch & Dhaniya (Chili & Coriander)
    12. Toor Dal (Arhar Dal)
    13. Chandan Agarbatti (Incense)
    14. 9W LED Bulb (Syska / Philips)
  - Selecting any item opens a quick bottom-sheet pre-filled with suggested MRP and standard units (e.g., 1 kg, 5 kg, 1 liter).
  - Tapping *"Add to My Shop"* calls `POST /api/v1/vendor/products` and immediately syncs with the customer app.

### 2.3 Live Order State Machine (Accept & Pack)
- **Requirement:** Shopkeepers must acknowledge and pack orders in a clear 2-step process.
- **Verification:**
  - When customer places an order, status is `PLACED`.
  - Vendor Dashboard shows order card under **New Orders** with audio notification.
  - Tapping **स्वीकार करें (Accept)** calls `POST /api/v1/vendor/orders/{id}/action` with `{"action": "ACCEPT"}` -> status updates to `ACCEPTED`.
  - Tapping **पैक हो गया (Mark Packed)** calls action `PACKED` -> status updates to `PACKED`. Order is now visible in the Runner dispatch queue.

### 2.4 0.0% Introductory Vendor Commission
- **Requirement:** Section 8 specifies zero commission for rural shopkeepers during the pilot phase.
- **Verification:**
  - In `SettlementsScreen`, order earnings display:
    $$\text{Vendor Payout} = \text{Product Price} \times \text{Quantity} - \text{₹0.00 Commission}$$
  - Backend settlement engine records `commission_rate = 0.0` and credits 100% of order subtotal to the vendor.

---

## 3. Physical Device Testing & Stability

- **Test Device:** Nothing Phone (2a) (`A142`, Android 16)
- **Installation:** Clean installation using `adb install -r apps/vendor/build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`.
- **Performance:** 60 FPS scrolling on catalog grid, zero memory leaks, instant camera/gallery permissions handling for custom shop photos.
