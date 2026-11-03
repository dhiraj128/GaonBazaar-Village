import pytest
from app.services.pricing_service import (
    calculate_delivery_fee,
    calculate_delivery_fee_paise,
    calculate_runner_payout,
    calculate_runner_payout_paise,
    calculate_platform_delivery_share,
    calculate_batch_payout,
    calculate_order_totals,
    ACTIVE_PRICING_POLICY
)
from app.core.config import settings

def test_proposed_five_tier_delivery_pricing():
    # 0 - 1 km -> ₹15.0 (1500 paise), Runner: ₹10.0, Platform: ₹5.0
    assert calculate_delivery_fee(0.8) == 15.0
    assert calculate_delivery_fee_paise(0.8) == 1500
    assert calculate_runner_payout(0.8) == 10.0
    assert calculate_runner_payout_paise(0.8) == 1000
    assert calculate_platform_delivery_share(0.8) == 5.0

    # > 1 - 2 km -> ₹20.0 (2000 paise), Runner: ₹14.0, Platform: ₹6.0
    assert calculate_delivery_fee(1.5) == 20.0
    assert calculate_runner_payout(1.5) == 14.0
    assert calculate_platform_delivery_share(1.5) == 6.0

    # > 2 - 4 km -> ₹25.0 (2500 paise), Runner: ₹18.0, Platform: ₹7.0
    assert calculate_delivery_fee(2.5) == 25.0
    assert calculate_runner_payout(2.5) == 18.0
    assert calculate_platform_delivery_share(2.5) == 7.0

    # > 4 - 6 km -> ₹30.0 (3000 paise), Runner: ₹22.0, Platform: ₹8.0
    assert calculate_delivery_fee(5.0) == 30.0
    assert calculate_runner_payout(5.0) == 22.0
    assert calculate_platform_delivery_share(5.0) == 8.0

    # > 6 - 8 km -> ₹40.0 (4000 paise), Runner: ₹28.0, Platform: ₹12.0
    assert calculate_delivery_fee(7.5) == 40.0
    assert calculate_runner_payout(7.5) == 28.0
    assert calculate_platform_delivery_share(7.5) == 12.0

def test_multi_order_batch_payout_algorithm():
    # Test batch of 3 orders over 4.5 km route
    batch = calculate_batch_payout(num_orders=3, route_distance_km=4.5)
    assert batch["num_orders"] == 3
    assert batch["route_distance_km"] == 4.5
    assert batch["base_pickup_rupees"] == 10.0
    assert batch["drop_fees_rupees"] == 24.0 # 3 * ₹8
    assert batch["distance_fee_rupees"] == 27.0 # 4.5 * ₹6
    assert batch["total_payout_rupees"] == 61.0 # 10 + 24 + 27
    assert batch["total_payout_paise"] == 6100

def test_strict_platform_fee_and_deterministic_totals():
    # Verify strict ₹3 platform fee
    assert settings.PLATFORM_FEE == 3.0
    
    subtotal = 200.0
    distance_km = 0.8 # Tier 1: ₹15 delivery fee
    totals = calculate_order_totals(subtotal, distance_km)
    
    assert totals["subtotal"] == 200.0
    assert totals["delivery_fee"] == 15.0
    assert totals["platform_fee"] == 3.0
    assert totals["total_amount"] == 218.0 # 200 + 15 + 3
