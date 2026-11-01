# GaonBazaar-Village — Render Staging Deployment & Infrastructure Guide

**Date:** 01 November 2026  
**New Repository:** `dhiraj128/GaonBazaar-Village` (Private, Branch: `main`)  
**Old Production Repository:** `dhiraj128/GaonBazar` — **STRICTLY UNTOUCHED**  
**Old Render Services:** `GaonBazar`, `gaonbazar-mobile-preview`, `gaonbazaar-db` — **STRICTLY UNTOUCHED & PRESERVED**  

---

## 1. Executive Summary

This document specifies the deployment architecture and execution steps for hosting the **GaonBazaar-Village** platform on Render as an independent, isolated staging environment. This enables the startup owner to access and test the **Super Admin website** and all **three native Android applications (Customer, Vendor, Runner)** over the public internet via Wi-Fi or mobile data without depending on a local laptop backend or USB ADB port forwarding.

---

## 2. Strict Production Isolation Guarantee

The owner's Render account already hosts:
- `GaonBazar` (`https://gaonbazar.onrender.com`)
- `gaonbazar-mobile-preview` (`https://gaonbazar-mobile-preview.onrender.com`)
- `gaonbazaar-db` (Existing PostgreSQL database)

### Isolation Rules:
1. **Zero Access:** No scripts, environment variables, connection strings, or deployment hooks in `GaonBazaar-Village` reference or connect to `gaonbazaar-db` or the old production web services.
2. **Independent Repositories:** All deployments originate exclusively from `dhiraj128/GaonBazaar-Village`.
3. **No Credential Sharing:** All JWT secrets, database connection strings, and admin session keys are generated afresh for `GaonBazaar-Village`.

---

## 3. Dedicated Render Services Architecture

### A. FastAPI Backend Web Service
- **Service Name:** `gaonbazaar-village-api`
- **Service Type:** Web Service
- **Runtime:** Python 3.12.7
- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Assigned Public URL:** `https://gaonbazaar-village-api.onrender.com`
- **Health Check Endpoint:** `GET /health` -> `{"status": "healthy", "commit": "c30afc3"}`
- **Auto-Deployment:** Triggered from `main` of `dhiraj128/GaonBazaar-Village`.

### B. Super Admin Dashboard Static Site
- **Service Name:** `gaonbazaar-village-admin`
- **Service Type:** Static Site
- **Root Directory:** `apps/admin`
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `dist`
- **Assigned Public URL:** `https://gaonbazaar-village-admin.onrender.com`
- **Route Rewrites:** `/*` -> `/index.html` (SPA routing)
- **Environment Variable:** `VITE_API_BASE_URL=https://gaonbazaar-village-api.onrender.com/api/v1`

---

## 4. Mandatory Database Isolation & Render Free-Tier Constraint

### Render Free-Tier Limit Analysis:
Render strictly enforces **one active Free PostgreSQL database per user/workspace account**. Because `gaonbazaar-db` is already actively running for the previous project, Render's API will reject any attempt to provision a second free PostgreSQL instance within the same workspace.

> [!CAUTION]
> In accordance with master instructions, database provisioning was **HALTED** from silently purchasing paid services or reusing the old database. The available isolated options are outlined below for owner authorization.

### Database Options & Cost Breakdown:

| Option | Architecture | Hosting Provider | Persistence | Monthly Cost | Action Required |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Option 1 (Recommended Paid)** | Render Starter PostgreSQL (`gaonbazaar-village-db`) | Render | 100% Persistent (1 GB RAM, 10 GB Storage) | **$7.00 / month** | Authorize creation of `gaonbazaar-village-db` in existing Render account. |
| **Option 2 (Zero Cost Render)** | Separate Free Render Workspace | Render (New Free Account) | 30-Day Renewable Free Tier (1 GB Storage) | **$0.00 / month** | Create a separate free Render team/account dedicated to `GaonBazaar-Village`. |
| **Option 3 (Zero Cost External)** | Managed External Cloud PostgreSQL | Supabase or Neon.tech | Permanent Cloud PostgreSQL (500 MB Free) | **$0.00 / month** | Provide connection string to `DATABASE_URL` in `gaonbazaar-village-api`. |

*Note: In the interim, the backend's `session.py` and `config.py` have been engineered with adaptive database dialect detection. As soon as a connection string is supplied in the Render Dashboard under `DATABASE_URL`, SQLAlchemy automatically connects via `postgresql+asyncpg://` with 0 code changes.*

---

## 5. HTTPS Mobile Access for Android Apps

All three Android applications have been reconfigured to communicate over secure HTTPS directly with the Render staging cloud:

### Base URL Resolution Hierarchy:
1. **Compile-Time Flag:** Passed via `--dart-define=API_BASE_URL=https://gaonbazaar-village-api.onrender.com/api/v1`.
2. **Release Build Default:** [`Endpoints.stagingBaseUrl`](file:///C:/Users/dhira/OneDrive/Desktop/GaoBazar-Village/packages/api_client/lib/src/endpoints.dart) defaults directly to `https://gaonbazaar-village-api.onrender.com/api/v1`.
3. **Cold-Start Handling:** Render free-tier web services sleep after 15 minutes of inactivity and take 20–30 seconds to spin up on the first request. The `api_client` has been upgraded with a 15-second health timeout and localized retry messages ("सर्वर से संपर्क में समय लग रहा है...").
4. **Zero Cleartext:** Release builds enforce TLS 1.3 / HTTPS encryption.

---

## 6. Staging Test Personas & Records

| Role | Test Mobile Number | Test OTP | Staging Profile Details | Primary Test Workflow |
| :--- | :--- | :--- | :--- | :--- |
| **Customer** | `9800000000` | `123456` | Sunil Kumar, Chaturshi, Minapur | Browse Minapur stores, cart items, place COD orders, track live status. |
| **Vendor** | `9800000001` | `123456` | Raju Sharma, Maa Sharda Kirana Store | Accept orders, mark packed, manage inventory stock, view 0% commission payouts. |
| **Runner** | `9800000003` | `123456` | Santosh Kumar, Hero Splendor (`BR-06-AB-1234`) | Accept delivery jobs, pickup, out-for-delivery, verify 4-digit PIN, collect COD cash. |
| **Super Admin** | Portal Access | Web Auth | Master Administrator | Approve new vendors & runners, monitor orders, configure fees, view audit logs. |

---

## 7. Step-by-Step Render Deployment Guide

### Step 1: Push Blueprint to Private GitHub
The repository contains the root [`render.yaml`](file:///C:/Users/dhira/OneDrive/Desktop/GaoBazar-Village/render.yaml) specification:
```bash
git push origin main
```

### Step 2: Connect Repository in Render Dashboard
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click **Blueprints** -> **New Blueprint Instance**.
3. Select the private repository: `dhiraj128/GaonBazaar-Village`.
4. Render will parse `render.yaml` and display the two configured services:
   - `gaonbazaar-village-api` (Web Service)
   - `gaonbazaar-village-admin` (Static Site)
5. Under environment variables for `gaonbazaar-village-api`, set `DATABASE_URL` to your selected database instance (from Option 1, 2, or 3).
6. Click **Apply**.

### Step 3: Verify Deployment Endpoints
Once the build completes:
- Backend Health Check: `https://gaonbazaar-village-api.onrender.com/health`
- Super Admin Dashboard: `https://gaonbazaar-village-admin.onrender.com`

---

## 8. Owner Verification Instructions (Over Wi-Fi & 4G Mobile Data)

1. **Install Release APKs on Physical Device:**
   Download the ARM64 release APKs (generated via split-per-abi) to the test phone.
2. **Disconnect USB & ADB Port Forwarding:**
   Unplug the USB cable from the PC. Ensure no `adb reverse` commands are running.
3. **Switch to 4G Cellular Mobile Data:**
   Enable mobile data (or standard home Wi-Fi) on the Nothing Phone (2a).
4. **Open GaonBazaar Customer App:**
   - Log in using test phone `9800000000` and OTP `123456`.
   - Add items to cart from "माँ शारदा किराना स्टोर" and place a COD order.
5. **Open GaonBazaar Vendor App:**
   - Log in using `9800000001` and OTP `123456`.
   - The new order appears under the "नया" (New) tab. Accept and mark "पैक हो गया" (Packed).
6. **Open GaonBazaar Runner App:**
   - Log in using `9800000003` and OTP `123456`.
   - The job appears under "उपलब्ध डिलीवरी कार्य". Accept, confirm pickup, and advance to "ग्राहक की ओर रवाना".
   - Enter the customer's 4-digit OTP code to complete delivery and collect COD cash.
7. **Inspect Super Admin Portal:**
   - Visit `https://gaonbazaar-village-admin.onrender.com` in Chrome/Safari.
   - Inspect the live order in "Live Order Monitor", check the completed GMV, and review the audit log.
