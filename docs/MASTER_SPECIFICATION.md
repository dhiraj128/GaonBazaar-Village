# GaonBazaar — Master Specification
**Village-Focused Hyperlocal Quick-Commerce Platform**
**Launch Focus:** Minapur Block, Muzaffarpur, Bihar (Pilot Localities: Chaturshi/Chatursi, Tubanaghara/Benaghara, Sivay Patti, Tulsi Ganj/Bangaon)

---

## 1. Executive Overview & Mission
GaonBazaar brings genuine quick-commerce (30-60 min delivery target) to rural communities. Unlike urban models that rely on dark stores, GaonBazaar digitizes verified local village kiranas, general stores, dairies, and vegetable sellers, pairing them with localized village delivery runners.

### Core Metrics & Enforced Boundaries
- **Maximum Delivery Radius:** 8.0 km (strictly calculated and enforced by backend via Haversine distance from vendor GPS to customer GPS).
- **Vendor Commission:** 0% introductory rate for village shopkeepers.
- **Platform Fee:** Fixed ₹3 per successful order.
- **Delivery Fee Engine:** Configurable by admin based on distance tier (e.g. ₹15 base up to 3 km, ₹5/km thereafter).
- **Runner Payout:** 100% of delivery fee plus operational incentives.
- **Customer Cancellation Window:** 180 seconds (3 minutes) strict backend countdown before order moves to store preparation.
- **Payment Modes:** Cash on Delivery (COD) and Online Payments (UPI / Card / NetBanking via authorized gateway integration).

---

## 2. Platform Architecture
The ecosystem consists of:
1. **Customer App (Android):** Multilingual (Hindi/English), Voice/Text AI shopping assistant, real stores, 2-column product grid, draggable pin map, live 7-stage order tracking.
2. **Vendor App (Android):** Store open/close toggle, quick-action incoming order management, pack & handoff workflows, centralized product library catalog with custom pricing, earnings dashboard.
3. **Runner App (Android):** Live delivery job broadcasts within 8 km, turn-by-turn navigation targets, store pickup confirmation, customer delivery OTP verification, daily cash/earnings summary.
4. **Super Admin Web Dashboard (React/TypeScript):** Real-time orders, vendor/runner KYC approvals, dynamic delivery zones, service area enforcement, refund & payout processing, catalog management, audit logs.
5. **Shared Backend (FastAPI + PostgreSQL):** Centralized REST API, WebSocket/real-time event streaming, role-based JWT auth, order state machine, distance geofencing, payment webhook handlers.
6. **Shared Packages:**
   - `design_system`: Standardized GaonBazaar brand green palette, Light/Dark theme tokens, typography, buttons, product cards, order status badges.
   - `api_client`: Type-safe HTTP and WebSocket client for the shared backend.
   - `shared_models`: Common serialization models for Users, Stores, Products, Carts, Orders, and Deliveries.
   - `localization`: Full bilingual (Hindi and English) dictionary and number formatting.

---

## 3. Product Catalog Rules
Supported Categories:
1. Grocery & Ration (Atta, Rice, Dal, Mustard Oil, Spices, Sugar, Salt)
2. Vegetables & Fruits (Potatoes, Onions, Tomatoes, Seasonal Produce)
3. Fresh Dairy & Eggs (Milk, Paneer, Curd, Ghee, Eggs)
4. Pooja & Ritual Essentials (Agarbatti, Camphor, Diya, Supari, Sindoor)
5. Electrical & Hardware (LED Bulbs, Tape, Sockets, Wires, Batteries)
6. General Store & Household (Soaps, Detergents, Oral Care, Mosquito coils, Matchboxes)

*Note:* Prepared hot restaurant food and mobile phone hardware are explicitly excluded from pilot phase.

---

## 4. Order Lifecycle State Machine
1. `PLACED`: Customer places order; 180-second countdown begins.
2. `ACCEPTED`: Vendor confirms availability and begins packing.
3. `PACKED`: Vendor finishes packing; system broadcasts job to nearby online runners.
4. `RUNNER_ASSIGNED`: Runner accepts delivery job.
5. `PICKED_UP`: Runner collects package from vendor with verification.
6. `OUT_FOR_DELIVERY`: Runner en route to customer destination.
7. `DELIVERED`: Runner enters the customer's 4-digit Delivery OTP to finalize order.
8. `CANCELLED`: Eligible only if triggered by customer within 180 seconds or rejected by vendor with cause.

---

## 5. Security & Rural Optimization Principles
- Low-bandwidth asset caching (optimized WebP product imagery, compressed payloads).
- Minimal GPS battery drain (dynamic polling intervals: 30s during active transit, idle otherwise).
- Strict backend role authorization (Customer, Vendor, Runner, Admin).
- Tamper-proof OTP verification for phone login and order delivery handoff.
