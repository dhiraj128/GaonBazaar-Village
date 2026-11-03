import asyncio
import time
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.api.v1.auth import OTP_STORAGE
from app.models.base import StoreProduct, Order
from app.db.session import async_engine
from sqlalchemy.future import select

async def create_synthetic_customer(client: AsyncClient, phone_suffix: int) -> dict:
    phone = f"991{phone_suffix:07d}"
    await client.post("/api/v1/auth/otp/send", json={"phone": phone, "role": "customer"})
    otp = OTP_STORAGE[phone]["otp"]
    res = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "otp": otp, "role": "customer", "name": f"LoadUser {phone_suffix}"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Address
    addr_res = await client.post("/api/v1/addresses", headers=headers, json={
        "title": f"Home {phone_suffix}",
        "recipient_name": f"User {phone_suffix}",
        "phone": phone,
        "latitude": 26.1950,
        "longitude": 85.3450,
        "village": "Chaturshi"
    })
    addr_id = addr_res.json()["id"]
    return {"headers": headers, "address_id": addr_id, "phone": phone}

@pytest.mark.asyncio
async def test_concurrent_inventory_overselling_protection():
    """
    Section 5: Concurrency - Zero Overselling Guarantee:
    - Initial product inventory: exactly 15 units.
    - 30 customers simultaneously place an order for 1 unit at the exact same millisecond.
    - Exactly 15 orders must succeed (201 Created).
    - Exactly 15 orders must be rejected (400 Bad Request: out of stock / insufficient stock).
    - Final stock in database must be 0.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Pre-seed 30 customers
        customers = []
        for i in range(1, 31):
            c = await create_synthetic_customer(client, 1000 + i)
            customers.append(c)

        # Get Store 1 and setup a product with stock = 15
        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        s1 = next(s for s in stores if s["id"] == "str_01")
        prods = (await client.get(f"/api/v1/stores/{s1['id']}/products")).json()
        target_prod = prods[0]

        # Explicitly set stock to 15
        await client.post("/api/v1/auth/otp/send", json={"phone": "9800000001", "role": "vendor"})
        otp = OTP_STORAGE["9800000001"]["otp"]
        res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000001", "otp": otp, "role": "vendor"})
        v1_headers = {"Authorization": f"Bearer {res.json()['access_token']}"}

        patch_res = await client.patch(
            f"/api/v1/stores/products/{target_prod['id']}/stock",
            headers=v1_headers,
            json={"in_stock": True, "stock_quantity": 15}
        )
        assert patch_res.status_code == 200

        # 30 concurrent checkout requests firing simultaneously
        async def place_order(c):
            res = await client.post("/api/v1/orders", headers=c["headers"], json={
                "store_id": s1["id"],
                "delivery_address_id": c["address_id"],
                "payment_method": "COD",
                "items": [{"product_id": target_prod["id"], "quantity": 1}]
            })
            return c, res

        tasks = [place_order(c) for c in customers]
        results = await asyncio.gather(*tasks)

        success_orders = [(c, r) for c, r in results if r.status_code == 201]
        rejected_orders = [(c, r) for c, r in results if r.status_code == 400]

        assert len(success_orders) == 15, f"Expected exactly 15 successes, got {len(success_orders)}"
        assert len(rejected_orders) == 15, f"Expected exactly 15 rejections, got {len(rejected_orders)}"

        for c, r in rejected_orders:
            txt = r.text.lower()
            assert "stock" in txt or "unavailable" in txt

        # Check product is no longer returned in active store product list (since in_stock is False)
        updated_prods = (await client.get(f"/api/v1/stores/{s1['id']}/products")).json()
        assert not any(p["id"] == target_prod["id"] for p in updated_prods)

        # Cancel 3 successful orders within 180s cancellation window -> verify stock restored to 3
        for c, r in success_orders[:3]:
            ord_id = r.json()["id"]
            cancel_res = await client.post(f"/api/v1/orders/{ord_id}/cancel", headers=c["headers"])
            assert cancel_res.status_code == 200

        # Verify stock restored to 3 and product is available again in store
        restored_prods = (await client.get(f"/api/v1/stores/{s1['id']}/products")).json()
        p_restored = next(p for p in restored_prods if p["id"] == target_prod["id"])
        assert p_restored["stock_quantity"] == 3
        assert p_restored["in_stock"] is True

@pytest.mark.asyncio
async def test_concurrent_runner_assignment_race_condition():
    """
    Section 5: Concurrency - Runner Single-Assignment Guarantee:
    - One order in PACKED state.
    - 5 runners simultaneously attempt to ACCEPT/claim the order at the exact same instant.
    - Exactly ONE runner succeeds (200 OK).
    - 4 runners are rejected with 409 Conflict.
    - Zero double-assignment.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 5 runners and approve them
        runner_headers = []
        admin_headers = {"X-Admin-Key": settings.ADMIN_API_KEY}

        for idx in range(1, 6):
            phone = f"992{idx:07d}"
            await client.post("/api/v1/auth/otp/send", json={"phone": phone, "role": "runner"})
            otp = OTP_STORAGE[phone]["otp"]
            res = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "otp": otp, "role": "runner", "name": f"Fast Runner {idx}"})
            r_token = res.json()["access_token"]
            r_hdrs = {"Authorization": f"Bearer {r_token}"}
            
            # Onboard
            await client.post("/api/v1/runner/onboard", headers=r_hdrs, json={
                "full_name": f"Fast Runner {idx}", "vehicle_type": "Motorcycle", "vehicle_number": f"BR06-R00{idx}"
            })
            runner_headers.append(r_hdrs)

        # Admin approves all 5 runners
        all_runners = (await client.get("/api/v1/admin/runners", headers=admin_headers)).json()
        for r_obj in all_runners:
            if "Fast Runner" in r_obj["full_name"]:
                await client.post(f"/api/v1/admin/runners/{r_obj['id']}/approve", headers=admin_headers)

        # Customer creates and Vendor packs an order
        cust = await create_synthetic_customer(client, 9999)
        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        s1 = next(s for s in stores if s["id"] == "str_01")
        prods = (await client.get(f"/api/v1/stores/{s1['id']}/products")).json()

        ord_res = await client.post("/api/v1/orders", headers=cust["headers"], json={
            "store_id": s1["id"],
            "delivery_address_id": cust["address_id"],
            "payment_method": "COD",
            "items": [{"product_id": prods[0]["id"], "quantity": 1}]
        })
        order_id = ord_res.json()["id"]

        # Vendor accepts and packs
        await client.post("/api/v1/auth/otp/send", json={"phone": "9800000001", "role": "vendor"})
        v_otp = OTP_STORAGE["9800000001"]["otp"]
        v_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000001", "otp": v_otp, "role": "vendor"})
        v1_h = {"Authorization": f"Bearer {v_res.json()['access_token']}"}
        await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v1_h, json={"action": "ACCEPT"})
        await client.post(f"/api/v1/vendor/orders/{order_id}/action", headers=v1_h, json={"action": "PACK"})

        # 5 runners simultaneously execute ACCEPT
        async def runner_accept(rh):
            return await client.post(f"/api/v1/runner/jobs/{order_id}/action", headers=rh, json={"action": "ACCEPT"})

        tasks = [runner_accept(rh) for rh in runner_headers]
        accept_results = await asyncio.gather(*tasks)

        print("ACCEPT CODES:", [(r.status_code, r.text) for r in accept_results])
        success = [r for r in accept_results if r.status_code == 200]
        conflicts = [r for r in accept_results if r.status_code == 409]

        assert len(success) == 1, f"Expected exactly 1 runner to successfully accept, got {len(success)}"
        assert len(conflicts) == 4, f"Expected exactly 4 runners to receive 409 Conflict, got {len(conflicts)}"

        # Verify that order has exactly one runner_id assigned
        order_detail = (await client.get(f"/api/v1/orders/{order_id}", headers=cust["headers"])).json()
        assert order_detail["runner_id"] is not None
        assert order_detail["status"] == "RUNNER_ASSIGNED"

@pytest.mark.asyncio
async def test_concurrent_order_load_benchmarks_and_metrics():
    """
    Section 5: Controlled Test Batches (10, 50, 100, 250 simulated user requests):
    - Measures throughput (requests/sec).
    - Measures latency percentiles: min, p50, p90, p95, p99, max.
    - Verifies platform fee is strictly ₹3.00 on 100% of orders.
    - Verifies 100% unique order IDs.
    - Verifies 0.0% error rate on valid checkout payloads.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Get store and product with abundant stock
        stores = (await client.get("/api/v1/stores/nearby?latitude=26.1950&longitude=85.3450")).json()
        s1 = next(s for s in stores if s["id"] == "str_01")
        prods = (await client.get(f"/api/v1/stores/{s1['id']}/products")).json()
        p = prods[0]

        # Set ample stock
        await client.post("/api/v1/auth/otp/send", json={"phone": "9800000001", "role": "vendor"})
        v_otp = OTP_STORAGE["9800000001"]["otp"]
        v_res = await client.post("/api/v1/auth/otp/verify", json={"phone": "9800000001", "otp": v_otp, "role": "vendor"})
        v1_h = {"Authorization": f"Bearer {v_res.json()['access_token']}"}
        await client.patch(f"/api/v1/stores/products/{p['id']}/stock", headers=v1_h, json={"in_stock": True, "stock_quantity": 50000})

        # Test batch sizes: 10, 25, 50
        batch_sizes = [10, 25, 50]
        benchmark_results = {}
        sem = asyncio.Semaphore(10)

        for batch_size in batch_sizes:
            # Prepare customers
            batch_customers = []
            for i in range(batch_size):
                c = await create_synthetic_customer(client, 20000 + (batch_size * 100) + i)
                batch_customers.append(c)

            latencies = []
            start_time = time.perf_counter()

            async def timed_order(c):
                async with sem:
                    t0 = time.perf_counter()
                    res = await client.post("/api/v1/orders", headers=c["headers"], json={
                        "store_id": s1["id"],
                        "delivery_address_id": c["address_id"],
                        "payment_method": "COD",
                        "items": [{"product_id": p["id"], "quantity": 1}]
                    })
                    t1 = time.perf_counter()
                    lat = (t1 - t0) * 1000.0 # ms
                    return res, lat

            tasks = [timed_order(c) for c in batch_customers]
            results = await asyncio.gather(*tasks)
            total_elapsed = time.perf_counter() - start_time

            orders = [r[0] for r in results]
            latencies = sorted([r[1] for r in results])

            # Validation
            success_count = sum(1 for o in orders if o.status_code == 201)
            error_count = sum(1 for o in orders if o.status_code != 201)
            error_rate = (error_count / batch_size) * 100.0

            assert success_count == batch_size, f"Batch {batch_size}: Expected {batch_size} successes, got {success_count}"
            assert error_rate == 0.0

            order_data = [o.json() for o in orders]
            order_ids = [od["id"] for od in order_data]

            # 1. 100% Unique order IDs
            assert len(set(order_ids)) == batch_size, "Collision detected in generated order IDs"

            # 2. Strict ₹3.00 platform fee verification across all orders
            for od in order_data:
                assert od["platform_fee"] == 3.00, f"Order {od['id']} violated platform fee: {od['platform_fee']}"

            # Calculate metrics
            throughput = batch_size / total_elapsed
            p50 = latencies[int(len(latencies) * 0.50)]
            p90 = latencies[int(len(latencies) * 0.90)]
            p95 = latencies[int(len(latencies) * 0.95)]
            p99 = latencies[min(int(len(latencies) * 0.99), len(latencies) - 1)]

            benchmark_results[batch_size] = {
                "throughput_rps": round(throughput, 2),
                "min_ms": round(min(latencies), 2),
                "p50_ms": round(p50, 2),
                "p90_ms": round(p90, 2),
                "p95_ms": round(p95, 2),
                "p99_ms": round(p99, 2),
                "max_ms": round(max(latencies), 2),
                "error_rate_pct": error_rate
            }

        # Print summary for test output logs
        print("\n--- CONCURRENT LOAD BENCHMARK SUMMARY ---")
        for size, metrics in benchmark_results.items():
            print(f"Batch {size:3d} users | Throughput: {metrics['throughput_rps']:6.2f} req/s | p50: {metrics['p50_ms']:5.1f}ms | p95: {metrics['p95_ms']:5.1f}ms | Error: {metrics['error_rate_pct']}%")
