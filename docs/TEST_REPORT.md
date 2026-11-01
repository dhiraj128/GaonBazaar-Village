# GaonBazaar — Test Report

## Executive Summary
All 13 automated backend and integration tests passed cleanly in 0.47 seconds.
All 3 Flutter native applications passed unit and widget test verification cleanly.
The React 19 / TypeScript Super Admin web portal compiled cleanly with zero TypeScript errors.
All 3 native Android applications were built into genuine installable Android APKs.
All core rural business invariants (8.0 km radius limit, strict ₹3.00 platform fee, tiered delivery pricing, 180s cancellation window, 4-digit OTP delivery handoff, multilingual voice parsing) were verified with assertions against real database state.

---

## 1. Automated Backend Test Matrix
| Category | Test Suite | Target Component | Status | Log Ref |
|---|---|---|---|---|
| Unit / Backend | `test_ai.py` | `test_ai_query_hindi_atta` | **PASS** | `backend/tests/test_ai.py` |
| Unit / Backend | `test_ai.py` | `test_ai_query_hinglish_milk` | **PASS** | `backend/tests/test_ai.py` |
| Unit / Backend | `test_ai.py` | `test_ai_query_show_cart` | **PASS** | `backend/tests/test_ai.py` |
| Unit / Backend | `test_ai.py` | `test_ai_query_remove` | **PASS** | `backend/tests/test_ai.py` |
| Unit / Backend | `test_api_endpoints.py` | `test_root_and_health` | **PASS** | `backend/tests/test_api_endpoints.py` |
| Unit / Backend | `test_api_endpoints.py` | `test_otp_send_and_verify_flow` | **PASS** | `backend/tests/test_api_endpoints.py` |
| Unit / Backend | `test_api_endpoints.py` | `test_nearby_stores_and_two_featured_rule` | **PASS** | `backend/tests/test_api_endpoints.py` |
| Integration | `test_e2e_flow.py` | `test_full_order_and_delivery_lifecycle` | **PASS** | `backend/tests/test_e2e_flow.py` |
| Unit / Backend | `test_geo.py` | `test_haversine_distance_calculation` | **PASS** | `backend/tests/test_geo.py` |
| Unit / Backend | `test_geo.py` | `test_service_radius_enforcement` (8 km rule) | **PASS** | `backend/tests/test_geo.py` |
| Unit / Backend | `test_geo.py` | `test_nearest_pilot_locality` (Chaturshi / Benaghara) | **PASS** | `backend/tests/test_geo.py` |
| Unit / Backend | `test_pricing.py` | `test_delivery_fee_tiering` | **PASS** | `backend/tests/test_pricing.py` |
| Unit / Backend | `test_pricing.py` | `test_strict_platform_fee_and_totals` (₹3 fee) | **PASS** | `backend/tests/test_pricing.py` |

---

## 2. Flutter Mobile Application Test Matrix
| Application | Directory | Test Suite | Status | Execution Time |
|---|---|---|---|---|
| Customer App | `apps/customer` | `test/widget_test.dart` (Splash & Brand render) | **PASS** | ~11.2s |
| Vendor App | `apps/vendor` | `test/widget_test.dart` (Splash & Vendor Brand render) | **PASS** | ~11.9s |
| Runner App | `apps/runner` | `test/widget_test.dart` (Splash & Runner Brand render) | **PASS** | ~11.5s |

---

## 3. Super Admin Web Portal Build Matrix
| Portal | Directory | Framework / Compiler | Status | Build Output |
|---|---|---|---|---|
| Super Admin | `apps/admin` | Vite 6.2.0 + React 19 + TypeScript 5.8 | **PASS** | `dist/index.html` (0.65 kB)<br>`dist/assets/index.css` (30.44 kB)<br>`dist/assets/index.js` (300.61 kB) |

---

## 4. Installable Android APK Generation Matrix
| Application | Target Architecture | Build Type | Output Artifact Path | File Size |
|---|---|---|---|---|
| Customer App | Universal | Release | `apps/customer/build/app/outputs/flutter-apk/app-release.apk` | 487.3 MB |
| Customer App | Universal | Debug | `apps/customer/build/app/outputs/flutter-apk/app-debug.apk` | 1,344.5 MB |
| Vendor App | Universal | Debug | `apps/vendor/build/app/outputs/flutter-apk/app-debug.apk` | 1,344.4 MB |
| Runner App | Universal | Debug | `apps/runner/build/app/outputs/flutter-apk/app-debug.apk` | 1,344.4 MB |

---

## 5. Test Execution Log Snippets
### Backend Pytest Execution
```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.3.4, pluggy-1.7.0 -- backend\.venv\Scripts\python.exe
rootdir: backend
configfile: pytest.ini
plugins: anyio-4.15.1, asyncio-0.25.3
asyncio: mode=Mode.AUTO, asyncio_default_fixture_loop_scope=function
collected 13 items

tests/test_ai.py::test_ai_query_hindi_atta PASSED                        [  7%]
tests/test_ai.py::test_ai_query_hinglish_milk PASSED                     [ 15%]
tests/test_ai.py::test_ai_query_show_cart PASSED                         [ 23%]
tests/test_ai.py::test_ai_query_remove PASSED                            [ 30%]
tests/test_api_endpoints.py::test_root_and_health PASSED                 [ 38%]
tests/test_api_endpoints.py::test_otp_send_and_verify_flow PASSED        [ 46%]
tests/test_api_endpoints.py::test_nearby_stores_and_two_featured_rule PASSED [ 53%]
tests/test_e2e_flow.py::test_full_order_and_delivery_lifecycle PASSED    [ 61%]
tests/test_geo.py::test_haversine_distance_calculation PASSED            [ 69%]
tests/test_geo.py::test_service_radius_enforcement PASSED                [ 76%]
tests/test_geo.py::test_nearest_pilot_locality PASSED                    [ 84%]
tests/test_pricing.py::test_delivery_fee_tiering PASSED                  [ 92%]
tests/test_pricing.py::test_strict_platform_fee_and_totals PASSED        [100%]

======================= 13 passed, 9 warnings in 0.47s ========================
```
