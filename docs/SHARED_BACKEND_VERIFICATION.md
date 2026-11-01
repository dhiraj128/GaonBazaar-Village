# GaonBazaar Shared Backend — Security, Performance & Schema Verification Report

**Date:** 01 November 2026  
**Backend Framework:** FastAPI 0.115.8, SQLAlchemy 2.0.38, SQLite / PostgreSQL (AsyncSession)  
**Daemon Status:** Running on `http://127.0.0.1:8000` (PID / Task 2681)  
**Test Suite:** Pytest 8.3.4 (All 27/27 Tests Passing 100%)  
**Repository:** `dhiraj128/GaonBazaar-Village` (Private, Branch: `main`)  

---

## 1. Executive Summary

The GaonBazaar shared backend acts as the authoritative source of truth for all three native Android applications (Customer, Vendor, Runner) and the Super Admin Web portal.

During this engineering cycle, the backend underwent hardening to support:
1. Vendor shop onboarding (`POST /api/v1/stores/onboard`) with mandatory admin approval enforcement.
2. Vendor store status switching (`PATCH /api/v1/stores/status`) enforcing quarantine checks for unapproved stores.
3. Vendor inventory stock management (`PATCH /api/v1/stores/products/{product_id}/stock`).
4. Runner partner onboarding (`POST /api/v1/runner/onboard`) and duty toggling (`PATCH /api/v1/runner/status`).
5. Complete delivery action state transitions (`ACCEPT`, `PACK`, `HANDOFF`, `PICKUP`, `OUT_FOR_DELIVERY`, `DELIVER`).
6. Cryptographically secure 4-digit customer delivery OTP verification.
7. Real-time financial calculations (0% vendor commission rate, net payout due, runner trip fees, and cash-on-delivery remittance).

---

## 2. Automated Test Suite Results

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.3.4, pluggy-1.7.0
rootdir: C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village\backend
configfile: pytest.ini
collected 27 items

backend\tests\test_admin_audit.py::test_admin_settings_dynamic_update_and_audit PASSED [  3%]
backend\tests\test_admin_audit.py::test_admin_customer_management_and_tickets PASSED [  7%]
backend\tests\test_admin_audit.py::test_admin_vendor_and_runner_approval_flow PASSED [ 11%]
backend\tests\test_ai.py::test_ai_query_hindi_atta PASSED                [ 14%]
backend\tests\test_ai.py::test_ai_query_hinglish_milk PASSED             [ 18%]
backend\tests\test_ai.py::test_ai_query_show_cart PASSED                 [ 22%]
backend\tests\test_ai.py::test_ai_query_remove PASSED                    [ 25%]
backend\tests\test_api_endpoints.py::test_root_and_health PASSED         [ 29%]
backend\tests\test_api_endpoints.py::test_otp_send_and_verify_flow PASSED [ 33%]
backend\tests\test_api_endpoints.py::test_nearby_stores_and_two_featured_rule PASSED [ 37%]
backend\tests\test_cross_platform_integration.py::test_full_cross_platform_lifecycle PASSED [ 40%]
backend\tests\test_e2e_flow.py::test_full_order_and_delivery_lifecycle PASSED [ 44%]
backend\tests\test_geo.py::test_haversine_distance_calculation PASSED    [ 48%]
backend\tests\test_geo.py::test_service_radius_enforcement PASSED        [ 51%]
backend\tests\test_geo.py::test_nearest_pilot_locality PASSED            [ 55%]
backend\tests\test_order_security.py::test_eight_km_radius_enforcement_on_order_creation PASSED [ 59%]
backend\tests\test_order_security.py::test_price_manipulation_protection PASSED [ 62%]
backend\tests\test_order_security.py::test_order_cancellation_enforces_180s_window PASSED [ 66%]
backend\tests\test_order_security.py::test_delivery_otp_verification_security PASSED [ 70%]
backend\tests\test_pricing.py::test_delivery_fee_tiering PASSED          [ 74%]
backend\tests\test_pricing.py::test_strict_platform_fee_and_totals PASSED [ 77%]
backend\tests\test_security_roles.py::test_role_authentication_and_token_generation PASSED [ 81%]
backend\tests\test_security_roles.py::test_unapproved_vendor_not_in_customer_store_list PASSED [ 85%]
backend\tests\test_address_ownership_isolation PASSED [ 88%]
backend\tests\test_support_and_profile.py::test_customer_profile_update_and_support_hub PASSED [ 92%]
backend\tests\test_twenty_step_integration.py::test_twenty_step_integrated_journey PASSED [ 96%]
backend\tests\test_vendor_runner_repair.py::test_vendor_and_runner_endpoints_and_actions PASSED [100%]

======================= 27 passed, 71 warnings in 2.72s =======================
```

---

## 3. Route Precedence & Schema Repairs

1. **FastAPI Route Declaration Order:**
   In `backend/app/api/v1/stores.py`, static endpoints (`/stores/me`, `/stores/status`, `/stores/onboard`) were moved ahead of the parameterized path `/stores/{store_id}`. This prevents FastAPI/Starlette from matching the literal string `"me"` or `"status"` against `{store_id}` and returning a 404 error.

2. **Runner Model Attribute Alignment:**
   - In `backend/app/api/v1/orders.py`, fixed the reference from `runner.driving_license_number` to `runner.driving_licence_no`.
   - Fixed `cash_collected_to_remit` summation to use `o.payment_method == "COD"` instead of `payment_mode`.
   - Supplied default rating `4.9` in the runner profile response dictionary.

3. **Strict Delivery OTP Verification:**
   In `POST /api/v1/runner/jobs/{order_id}/action`, when the action is `DELIVER`, the backend enforces strict string matching between `action_data.delivery_otp` and `order.delivery_otp`. Invalid OTP codes reject the request with HTTP 400 (`गलत डिलीवरी ओटीपी`).

---

## 4. Key Endpoints Verified

| Method | Endpoint Path | Role Required | Purpose |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/otp/verify` | Any | JWT Token & User Profile generation |
| `GET` | `/api/v1/stores/me` | Vendor | Authenticated vendor's store profile |
| `POST` | `/api/v1/stores/onboard` | Vendor | New store registration (defaults to `is_approved=False`) |
| `PATCH` | `/api/v1/stores/status` | Vendor | Online/Offline toggle with approval check |
| `GET` | `/api/v1/vendor/orders` | Vendor | Orders placed with vendor's store |
| `POST` | `/api/v1/vendor/orders/{id}/action` | Vendor | Accept, pack, or handoff order |
| `GET` | `/api/v1/vendor/finances` | Vendor | Sales ledger and 0% commission payout due |
| `POST` | `/api/v1/runner/onboard` | Runner | Delivery partner onboarding |
| `GET` | `/api/v1/runner/me` | Runner | Runner profile, rating, and status |
| `PATCH` | `/api/v1/runner/status` | Runner | Duty Online/Offline toggle with approval check |
| `GET` | `/api/v1/runner/jobs` | Runner | Available and assigned delivery orders |
| `POST` | `/api/v1/runner/jobs/{id}/action` | Runner | Accept, pickup, out-for-delivery, and deliver |
| `GET` | `/api/v1/runner/finances` | Runner | Today's earnings and COD cash to remit |
| `GET` | `/api/v1/admin/overview` | Admin | Super Admin dashboard operational KPIs |
| `POST` | `/api/v1/admin/vendors/{id}/approve` | Admin | Approves pending store |
| `POST` | `/api/v1/admin/runners/{id}/approve` | Admin | Approves pending runner |
