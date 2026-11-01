# GaonBazaar — Database Design Schema

## Entity Relationship Overview
The database is structured to support relational integrity, geolocation queries, role segregation, and tamper-proof financial ledgers.

```
+---------------+       +------------------+       +------------------+
|     Users     | <---> | Addresses        |       | ServiceZones     |
+---------------+       +------------------+       +------------------+
  ^       ^
  |       |
  v       v
+-----------+   +-------------+   +-------------------+
|  Vendors  |   |   Runners   |   | GlobalCatalog     |
+-----------+   +-------------+   +-------------------+
  |               |                 |
  v               |                 v
+-----------+     |               +-------------------+
|  Stores   |     |               | StoreProducts     |
+-----------+     |               +-------------------+
  |               |                 |
  v               v                 v
+-------------------------------------+
|               Orders                |
+-------------------------------------+
  |                                 |
  v                                 v
+------------------+       +------------------+
|   OrderItems     |       | OrderTimeline    |
+------------------+       +------------------+
  |                                 |
  v                                 v
+------------------+       +------------------+
| PayoutLedger     |       | AuditLogs        |
+------------------+       +------------------+
```

---

## Table Definitions

### 1. `users`
- `id` (VARCHAR PK, uuid)
- `phone` (VARCHAR(15) UNIQUE NOT NULL)
- `name` (VARCHAR(100))
- `role` (ENUM: 'customer', 'vendor', 'runner', 'admin')
- `preferred_language` (VARCHAR(5) DEFAULT 'hi')
- `is_active` (BOOLEAN DEFAULT TRUE)
- `created_at` (TIMESTAMP WITH TIME ZONE)
- `updated_at` (TIMESTAMP WITH TIME ZONE)

### 2. `addresses`
- `id` (VARCHAR PK, uuid)
- `user_id` (VARCHAR FK -> users.id)
- `title` (VARCHAR(50)) -- Home, Shop, Other
- `recipient_name` (VARCHAR(100))
- `phone` (VARCHAR(15))
- `latitude` (DOUBLE PRECISION NOT NULL)
- `longitude` (DOUBLE PRECISION NOT NULL)
- `village` (VARCHAR(100) NOT NULL)
- `landmark` (VARCHAR(150))
- `block` (VARCHAR(100) DEFAULT 'Minapur')
- `district` (VARCHAR(100) DEFAULT 'Muzaffarpur')
- `state` (VARCHAR(50) DEFAULT 'Bihar')
- `is_default` (BOOLEAN DEFAULT FALSE)

### 3. `vendors` & `stores`
- `vendor_id` (VARCHAR PK -> users.id)
- `shop_name` (VARCHAR(150) NOT NULL)
- `owner_name` (VARCHAR(100) NOT NULL)
- `category` (VARCHAR(50) NOT NULL)
- `latitude` (DOUBLE PRECISION NOT NULL)
- `longitude` (DOUBLE PRECISION NOT NULL)
- `village` (VARCHAR(100) NOT NULL)
- `landmark` (VARCHAR(150))
- `is_online` (BOOLEAN DEFAULT TRUE)
- `is_approved` (BOOLEAN DEFAULT FALSE)
- `commission_rate` (DECIMAL(5,2) DEFAULT 0.0)
- `bank_payout_info` (JSONB)

### 4. `runners`
- `runner_id` (VARCHAR PK -> users.id)
- `full_name` (VARCHAR(100) NOT NULL)
- `vehicle_type` (VARCHAR(30)) -- motorcycle, bicycle
- `vehicle_number` (VARCHAR(30))
- `driving_licence_no` (VARCHAR(50))
- `is_online` (BOOLEAN DEFAULT FALSE)
- `is_approved` (BOOLEAN DEFAULT FALSE)
- `current_latitude` (DOUBLE PRECISION)
- `current_longitude` (DOUBLE PRECISION)
- `payout_info` (JSONB)

### 5. `global_catalog`
- `id` (VARCHAR PK)
- `name_en` (VARCHAR(150) NOT NULL)
- `name_hi` (VARCHAR(150) NOT NULL)
- `category` (VARCHAR(50) NOT NULL)
- `default_unit` (VARCHAR(30) NOT NULL) -- 1 kg, 500 g, 1 packet, etc.
- `suggested_mrp` (DECIMAL(10,2))
- `image_url` (VARCHAR(500) NOT NULL)

### 6. `store_products`
- `id` (VARCHAR PK)
- `store_id` (VARCHAR FK -> stores.id)
- `global_product_id` (VARCHAR FK -> global_catalog.id, NULLABLE for custom products)
- `custom_name_en` (VARCHAR(150))
- `custom_name_hi` (VARCHAR(150))
- `unit` (VARCHAR(30) NOT NULL)
- `price` (DECIMAL(10,2) NOT NULL)
- `mrp` (DECIMAL(10,2))
- `in_stock` (BOOLEAN DEFAULT TRUE)
- `stock_quantity` (INTEGER DEFAULT 100)

### 7. `orders`
- `id` (VARCHAR PK)
- `customer_id` (VARCHAR FK -> users.id)
- `store_id` (VARCHAR FK -> stores.id)
- `runner_id` (VARCHAR FK -> runners.id, NULLABLE)
- `status` (ENUM: 'PLACED', 'ACCEPTED', 'PACKED', 'RUNNER_ASSIGNED', 'PICKED_UP', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED')
- `delivery_address_id` (VARCHAR FK -> addresses.id)
- `subtotal` (DECIMAL(10,2) NOT NULL)
- `delivery_fee` (DECIMAL(10,2) NOT NULL)
- `platform_fee` (DECIMAL(10,2) DEFAULT 3.00)
- `total_amount` (DECIMAL(10,2) NOT NULL)
- `payment_method` (ENUM: 'COD', 'ONLINE')
- `payment_status` (ENUM: 'PENDING', 'PAID', 'FAILED', 'REFUNDED')
- `delivery_otp` (VARCHAR(6) NOT NULL)
- `placed_at` (TIMESTAMP WITH TIME ZONE NOT NULL)
- `cancel_until` (TIMESTAMP WITH TIME ZONE NOT NULL) -- placed_at + 180 seconds
- `delivered_at` (TIMESTAMP WITH TIME ZONE)
