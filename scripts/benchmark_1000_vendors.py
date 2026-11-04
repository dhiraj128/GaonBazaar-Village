import sys
import os
sys.path.insert(0, os.path.abspath('backend'))

import asyncio
import time
import statistics
from httpx import AsyncClient, ASGITransport
from app.main import app

async def run_benchmark():
    print("=" * 60)
    print("GAONBAZAAR PHASE 11: 1,000 VENDOR CATALOG BENCHMARK")
    print("=" * 60)

    latencies = []
    errors = 0
    total_requests = 1000
    concurrency = 20

    semaphore = asyncio.Semaphore(concurrency)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", timeout=30.0) as client:
        # Pre-warm: ensure app and DB are initialized
        warm = await client.get("/health")
        assert warm.status_code == 200

        async def worker(idx):
            nonlocal errors
            async with semaphore:
                start = time.perf_counter()
                try:
                    # Alternating between store queries and catalog queries
                    if idx % 2 == 0:
                        resp = await client.get("/api/v1/stores/str_01/products")
                    else:
                        resp = await client.get("/api/v1/stores/nearby?latitude=26.2315&longitude=85.3610")
                    dur = (time.perf_counter() - start) * 1000.0 # ms
                    if resp.status_code == 200:
                        latencies.append(dur)
                    else:
                        errors += 1
                except Exception as e:
                    errors += 1

        overall_start = time.perf_counter()
        tasks = [worker(i) for i in range(total_requests)]
        await asyncio.gather(*tasks)
        total_time = time.perf_counter() - overall_start

    throughput = len(latencies) / total_time if total_time > 0 else 0
    p50 = statistics.median(latencies) if latencies else 0
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else p50
    p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else p95
    avg_latency = statistics.mean(latencies) if latencies else 0

    print(f"Total Requests:      {total_requests}")
    print(f"Successful Requests: {len(latencies)}")
    print(f"Failed Requests:     {errors} (Error Rate: {(errors/total_requests)*100:.2f}%)")
    print(f"Total Duration:      {total_time:.2f} seconds")
    print(f"Throughput:          {throughput:.2f} req/sec")
    print(f"Avg Latency:         {avg_latency:.2f} ms")
    print(f"P50 Latency:         {p50:.2f} ms")
    print(f"P95 Latency:         {p95:.2f} ms")
    print(f"P99 Latency:         {p99:.2f} ms")
    print("=" * 60)

    # Strict SLA Assertions
    assert errors == 0, f"Expected 0 errors, got {errors}"
    assert p95 < 150.0, f"P95 latency {p95:.2f}ms exceeds 150ms SLA"
    print("ALL SCALE & BENCHMARK ASSERTIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
