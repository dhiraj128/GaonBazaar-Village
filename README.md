# GaonBazaar — Rural Hyperlocal Delivery Platform

GaonBazaar is a production-oriented delivery startup platform tailored specifically for rural India, launched initially in Minapur Block, Muzaffarpur, Bihar.

## Platform Components
- **`apps/customer`**: Native Android app for village shoppers (Hindi/English, voice AI assistant, live order tracking).
- **`apps/vendor`**: Native Android app for village shopkeepers (inventory, quick order accept/pack, centralized product library).
- **`apps/runner`**: Native Android app for local delivery partners (job alerts, route guidance, customer OTP verification).
- **`apps/admin`**: Web portal for operations, KYC approvals, live order map, delivery fee configuration.
- **`backend`**: Shared FastAPI backend with PostgreSQL/SQLite, geofencing (8 km cutoff), order state machine, payment processing.
- **`packages/`**:
  - `design_system`: GaonBazaar custom green brand design tokens & UI widgets.
  - `localization`: Bilingual Hindi / English string resources.
  - `shared_models`: Common Dart data models.
  - `api_client`: Unified HTTP/WebSocket network layer.

## Quick Start
### Backend
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Admin Portal
```bash
cd apps/admin
npm install
npm run dev
```

### Flutter Apps
```bash
# Customer App
cd apps/customer
flutter run

# Vendor App
cd apps/vendor
flutter run

# Runner App
cd apps/runner
flutter run
```
