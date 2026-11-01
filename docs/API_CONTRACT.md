# GaonBazaar — API Contract Specification
**Base URL:** `http://localhost:8000/api/v1`
**Protocol:** REST (JSON) + WebSocket for live tracking

---

## 1. Authentication & Users
### `POST /auth/otp/send`
- **Request Body:** `{ "phone": "9876543210", "role": "customer" | "vendor" | "runner" }`
- **Response 200:** `{ "message": "OTP sent successfully", "session_id": "sess_abc123", "expires_in": 300 }`

### `POST /auth/otp/verify`
- **Request Body:** `{ "phone": "9876543210", "otp": "123456", "session_id": "sess_abc123" }`
- **Response 200:**
  ```json
  {
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "user": {
      "id": "usr_01",
      "phone": "9876543210",
      "role": "customer",
      "name": "Ramesh Kumar",
      "is_active": true
    }
  }
  ```

---

## 2. Addresses & Geocoding
### `POST /addresses`
- **Headers:** `Authorization: Bearer <token>`
- **Request Body:**
  ```json
  {
    "title": "Home",
    "recipient_name": "Ramesh Kumar",
    "phone": "9876543210",
    "latitude": 26.2153,
    "longitude": 85.3456,
    "village": "Chaturshi",
    "landmark": "Near Shiv Mandir",
    "block": "Minapur",
    "district": "Muzaffarpur",
    "is_default": true
  }
  ```
- **Response 201:** Created address object.

### `GET /addresses`
- **Headers:** `Authorization: Bearer <token>`
- **Response 200:** Array of saved addresses for user.

### `POST /serviceability/check`
- **Request Body:** `{ "latitude": 26.2153, "longitude": 85.3456, "store_id": "str_01" }`
- **Response 200:**
  ```json
  {
    "is_serviceable": true,
    "distance_km": 3.42,
    "max_allowed_km": 8.0,
    "estimated_delivery_minutes": 35
  }
  ```

---

## 3. Stores & Products
### `GET /stores/nearby`
- **Query Params:** `latitude=26.2153&longitude=85.3456&radius_km=8.0`
- **Response 200:** Array of stores within 8km, sorting by distance and active status. Exactly returns featured stores flag.

### `GET /stores/{store_id}`
- **Response 200:** Detailed store profile, operational timings, active status.

### `GET /stores/{store_id}/products`
- **Response 200:** Products listed by store with current vendor price and inventory count.

### `GET /catalog/global`
- **Response 200:** Master catalog items for quick-add by vendors (standard imagery, categories, suggested units).

---

## 4. Cart & Checkout
### `POST /cart/sync`
- **Request Body:**
  ```json
  {
    "store_id": "str_01",
    "items": [
      { "product_id": "prd_01", "quantity": 2 }
    ]
  }
  ```
- **Response 200:** Validated items, item subtotals, delivery_fee (calculated), platform_fee (₹3.00), total_amount.

### `POST /orders`
- **Request Body:**
  ```json
  {
    "store_id": "str_01",
    "delivery_address_id": "addr_01",
    "payment_method": "COD" | "ONLINE",
    "items": [{ "product_id": "prd_01", "quantity": 2 }],
    "customer_notes": "Call near banyan tree"
  }
  ```
- **Response 201:** Created order object with status `PLACED`, `cancel_window_seconds_remaining`: 180, and `delivery_otp` (for customer receipt).

---

## 5. Orders Lifecycle
### `GET /orders/{order_id}`
- **Response 200:** Full order state, timeline items, runner details (if assigned), vendor details.

### `POST /orders/{order_id}/cancel`
- **Request Body:** `{ "reason": "Accidental order" }`
- **Behavior:** Backend strictly validates that current timestamp <= `placed_at + 180s`. If >180s, returns 400 Bad Request.

### `POST /vendor/orders/{order_id}/action`
- **Request Body:** `{ "action": "ACCEPT" | "REJECT" | "PACKED", "reason": "..." }`

### `POST /runner/jobs/{order_id}/action`
- **Request Body:** `{ "action": "ACCEPT" | "PICKUP" | "DELIVER", "delivery_otp": "4821" }`
- **Behavior:** `DELIVER` requires matching `delivery_otp`.

---

## 6. AI Voice Assistant
### `POST /ai/query`
- **Request Body:** `{ "text": "do kilo aata add karo", "store_id": "str_01" }`
- **Response 200:**
  ```json
  {
    "intent": "ADD_TO_CART",
    "matched_product": {
      "id": "prd_atta",
      "name": "Chakki Atta",
      "unit": "1 kg",
      "price": 38.0
    },
    "quantity": 2,
    "confidence": 0.95,
    "reply_text": "चक्की आटा 2 किलो आपके कार्ट में जोड़ दिया गया है।"
  }
  ```
