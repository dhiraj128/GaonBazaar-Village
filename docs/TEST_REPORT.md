# GaonBazaar — Test Report

## Executive Summary
All 13 automated backend and integration tests passed cleanly in 0.47 seconds.
All core rural business invariants (8.0 km radius limit, strict ₹3.00 platform fee, tiered delivery pricing, 180s cancellation window, 4-digit OTP delivery handoff, multilingual voice parsing) were verified with assertions against real database state.

---

## 1. Automated Test Matrix
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

## 2. Test Execution Log Snippet
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
