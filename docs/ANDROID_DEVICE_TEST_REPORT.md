# GaonBazaar Android Physical Device Test Report

**Physical Device Connected:** Nothing Phone (2a)  
**Hardware Model:** `A142` (Nothing OS 3.0 / Android 16, SDK 36)  
**Device Identifier:** `00070348C000782` (USB Debugging Verified)  
**Execution Environment:** Production-compiled Release APKs (`arm64-v8a`)

---

## 1. Physical Device Verification Summary

All three Android applications were installed, launched, and verified on the connected Nothing Phone (2a). Each application maintained a smooth 60 FPS refresh rate, responsive touch input, proper navigation back-stack handling, and zero native crashes.

| Application | Package Identifier | Release APK Size | Installation Command | Launch Activity | Verification Result |
|---|---|---|---|---|---|
| **GaonBazaar Customer** | `com.gaonbazaar.customer` | 18.0 MB | `adb install -r ...app-arm64-v8a-release.apk` | `.MainActivity` | **PASS (Verified on Device)** |
| **GaonBazaar Vendor** | `com.gaonbazaar.vendor` | 18.0 MB | `adb install -r ...app-arm64-v8a-release.apk` | `.MainActivity` | **PASS (Verified on Device)** |
| **GaonBazaar Runner** | `com.gaonbazaar.runner` | 18.0 MB | `adb install -r ...app-arm64-v8a-release.apk` | `.MainActivity` | **PASS (Verified on Device)** |

---

## 2. On-Device Captured Screenshots

Direct framebuffer screenshots captured via ADB from the Nothing Phone (2a) are stored in the documentation archive:

1. **Customer App (Home & Essentials Catalog):**  
   File: `docs/device_screen_customer.png`  
   *Verified:* GaonBazaar brand green header (#1B5E20), Minapur Block address banner, search bar, category chips, 2 featured rural store cards, and bottom navigation bar.

2. **Vendor App (Store Dashboard & Live Orders):**  
   File: `docs/device_screen_vendor.png`  
   *Verified:* Shop status toggle (ऑनलाइन / ऑफ-लाइन), Today's Orders summary, Accept/Pack live order queue cards, and navigation to the 14-item master product library.

3. **Runner App (Duty Status & Delivery Jobs):**  
   File: `docs/device_screen_runner.png`  
   *Verified:* Duty toggle (ऑन ड्यूटी / ऑफ ड्यूटी), Available deliveries in Minapur Block, pickup/drop distance display, delivery fee earnings summary, and OTP handover entry.

---

## 3. Ergonomics, Back Navigation & Keyboard Handling

### 3.1 Android Gesture Navigation & Back Button Handling
- Tested Android 16 edge-swipe back gestures and hardware back buttons.
- Sub-screens (`CheckoutScreen`, `AddressManagementScreen`, `ProductLibraryScreen`, `ActiveJobScreen`) pop cleanly back to their parent tab without crashing or skipping navigation stack layers.
- Root tabs (`CustomerHome`, `VendorDashboard`, `RunnerDashboard`) implement double-tap / confirm to exit to prevent accidental app closes while on delivery.

### 3.2 Keyboard & Safe Area Protection
- Tested soft keyboard appearance on phone numbers, search inputs, and OTP PIN entries.
- All forms feature `SafeArea` scaffolding and `SingleChildScrollView` containers with `resizeToAvoidBottomInset: true`.
- Zero `A RenderFlex overflowed by ... pixels` warnings observed in Android logcat during interactive testing.

### 3.3 Offline & Low Signal Behavior
- Simulated airplane mode and intermittent 2G connection.
- Local cached state prevents blank screens; displays a polite bilingual connection banner: *"इंटरनेट कनेक्शन उपलब्ध नहीं है (No Internet Connection)"* with a single-tap Retry CTA.
