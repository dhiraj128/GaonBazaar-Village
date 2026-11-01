# GaonBazaar — Release Checklist

## 1. Security & Compliance
- [ ] No hardcoded passwords, API secrets, or private keys in repository.
- [ ] OTP rate-limiting and session expiration enforced.
- [ ] Role-based access control verified on every backend route.
- [ ] 8.0 km maximum delivery distance verified on server side.
- [ ] Customer order cancellation strictly limited to 180 seconds.
- [ ] Runner delivery finalization requires valid 4-digit customer OTP.

## 2. Rural Device Optimization (Low RAM 3-4 GB & 4G Connectivity)
- [ ] Lightweight APK sizes measured.
- [ ] Images optimized and served with proper caching headers.
- [ ] Network failure graceful retries with user-friendly Hindi & English messages.
- [ ] Battery-friendly location requests (GPS polling stopped when idle).
- [ ] Smooth 60fps scrolling without UI thread stutter.

## 3. Localization & Usability
- [ ] 100% UI strings localized in Hindi and English.
- [ ] Language toggle persistent in device preferences.
- [ ] Voice input accepts mixed Hinglish/Hindi/English without restricting microphone locale.
- [ ] Android native Back button navigation verified on all screens.
- [ ] Map location shows readable village, landmark, block, and district names.

## 4. Platform Deployment
- [ ] FastAPI backend tests 100% passing.
- [ ] React Super Admin compiles cleanly.
- [ ] Customer, Vendor, and Runner Android APKs generated and verified.
