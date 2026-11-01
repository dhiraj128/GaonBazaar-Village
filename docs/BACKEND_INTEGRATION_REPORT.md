# GaonBazaar Backend & API Integration Report

**Framework:** FastAPI 0.115.x / Python 3.12  
**Database Architecture:** SQLAlchemy 2.0 Async (SQLite in development/test, PostgreSQL in production)  
**Security & Auth:** Python-Jose JWT (RS256/HS256), passlib bcrypt, Bearer Token Scheme  
**Test Suite Status:** 24 of 24 tests passing (100% Green)

---

## 1. Architecture & Router Topology

The backend is structured into modular API domains under `/api/v1/`:

```text
backend/app/
├── api/
│   └── v1/
│       ├── auth.py          # OTP login, role assignment, JWT issuance
│       ├── stores.py        # Store onboarding, product management, nearby discovery
│       ├── orders.py        # Order placement, 8km geofence, 180s cancel, vendor/runner actions
│       ├── admin.py         # Super admin approvals, settings, catalog, settlements
│       ├── geo.py           # Haversine distance, pilot localities, geofence checks
│       └── ai.py            # Natural language & voice shopping assistant NLP
├── core/
│   ├── config.py        # Environment settings (Pydantic Settings)
│   └── security.py      # JWT creation, decode, role-based dependencies
├── db/
│   └── session.py       # Async engine & sessionmaker
├── models/
│   └── base.py          # SQLAlchemy ORM models (User, Store, Runner, Order, etc.)
└── services/
    ├── geo_service.py       # Haversine formula & 8.0 km radius validation
    ├── pricing_service.py   # Tiered delivery fee, strict ₹3 fee, totals
    └── ai_service.py        # Fuzzy search & bilingual regex intent parser
```

---

## 2. Comprehensive Test Suite Execution (24/24 PASS)

The test suite executes against an isolated async in-memory SQLite database (`sqlite+aiosqlite:///:memory:`).

```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-8.3.4, pluggy-1.7.0
rootdir: C:\Users\dhira\OneDrive\Desktop\GaoBazar-Village\backend
configfile: pytest.ini
plugins: anyio-4.15.1, asyncio-0.25.3
collected 24 items

backend/tests/test_admin_audit.py::test_admin_settings_dynamic_update_and_audit PASSED [  4%]
backend/tests/test_admin_audit.py::test_admin_customer_management_and_tickets PASSED   [  8%]
backend/tests/test_admin_audit.py::test_admin_vendor_and_runner_approval_flow PASSED   [ 12%]
backend/tests/test_ai.py::test_ai_query_hindi_atta PASSED                              [ 16%]
backend/tests/test_ai.py::test_ai_query_hinglish_milk PASSED                           [ 20%]
backend/tests/test_ai.py::test_ai_query_show_cart PASSED                               [ 25%]
backend/tests/test_ai.py::test_ai_query_remove PASSED                                  [ 29%]
backend/tests/test_api_endpoints.py::test_root_and_health PASSED                       [ 33%]
backend/tests/test_api_endpoints.py::test_otp_send_and_verify_flow PASSED               [ 37%]
backend/tests/test_api_endpoints.py::test_nearby_stores_and_two_featured_rule PASSED   [ 41%]
backend/tests/test_e2e_flow.py::test_full_order_and_delivery_lifecycle PASSED         [ 45%]
backend/tests/test_geo.py::test_haversine_distance_calculation PASSED                  [ 50%]
backend/tests/test_geo.py::test_service_radius_enforcement PASSED                      [ 54%]
backend/tests/test_geo.py::test_nearest_pilot_locality PASSED                          [ 58%]
backend/tests/test_order_security.py::test_eight_km_radius_enforcement_on_order_creation PASSED [ 62%]
backend/tests/test_order_security.py::test_price_manipulation_protection PASSED         [ 66%]
backend/tests/test_order_security.py::test_order_cancellation_enforces_180s_window PASSED [ 70%]
backend/tests/test_order_security.py::test_delivery_otp_verification_security PASSED  [ 75%]
backend/tests/test_pricing.py::test_delivery_fee_tiering PASSED                        [ 79%]
backend/tests/test_pricing.py::test_strict_platform_fee_and_totals PASSED             [ 83%]
backend/tests/test_security_roles.py::test_role_authentication_and_token_generation PASSED [ 87%]
backend/tests/test_security_roles.py::test_unapproved_vendor_not_in_customer_store_list PASSED [ 91%]
backend/tests/test_security_roles.py::test_address_ownership_isolation PASSED         [ 95%]
backend/tests/test_twenty_step_integration.py::test_twenty_step_integrated_journey PASSED [100%]

======================= 24 passed, 39 warnings in 1.06s =======================
```

---

## 3. Core Business & Security Rules Verified

### 3.1 Strict 8.0 km Geofencing
- Implemented in `services/geo_service.py` using the Haversine equation:
  $$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$
- If distance $> 8.0\text{ km}$, order creation is rejected immediately with HTTP 400.

### 3.2 Price Manipulation Protection
- In `POST /api/v1/orders`, the client payload only supplies `{ "product_id": "...", "quantity": 2 }`.
- The backend queries the database for the current approved vendor product price and recalculates the line total. Client cannot spoof or inject custom prices.

### 3.3 Strict 180s Cancellation Window
- Calculated at order creation: `cancel_until = placed_at + timedelta(seconds=180)`.
- If an order is in `PLACED` state and `now() <= cancel_until`, cancellation is approved with full refund. Past 180s, the order transitions to irreversible fulfillment.

### 3.4 4-Digit Delivery OTP Cryptographic Check
- On order creation, a 4-digit numeric OTP is randomly generated (`f"{random.randint(1000, 9999)}"`) and stored in the order record.
- Displayed only to the ordering customer.
- Delivery runner MUST provide the correct OTP via `POST /api/v1/runner/jobs/{id}/action` with action `DELIVER`. Mismatched OTP returns HTTP 400.
