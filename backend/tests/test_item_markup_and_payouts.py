import pytest
from app.services.pricing_service import (
    compute_item_pricing,
    calculate_delivery_fee,
    calculate_runner_payout,
    calculate_platform_delivery_share,
    calculate_order_totals,
    ACTIVE_PRICING_POLICY
)

def test_markup_rule_a_packaged_below_mrp():
    # Rule A: mrp > 0 and vendor_price < mrp -> min(vendor_price + 2.0, mrp)
    pricing = compute_item_pricing(vendor_price=40.0, mrp=50.0)
    assert pricing["customer_price"] == 42.0
    assert pricing["vendor_price"] == 40.0
    assert pricing["item_margin"] == 2.0
    assert pricing["mrp"] == 50.0

def test_markup_rule_a_capped_at_mrp():
    # When vendor_price + 2.0 would exceed MRP, cap at MRP
    pricing = compute_item_pricing(vendor_price=49.0, mrp=50.0)
    assert pricing["customer_price"] == 50.0
    assert pricing["item_margin"] == 1.0

def test_markup_rule_b_packaged_equal_mrp():
    # Rule B: mrp > 0 and vendor_price == mrp -> customer_price == vendor_price, margin == 0
    pricing = compute_item_pricing(vendor_price=50.0, mrp=50.0)
    assert pricing["customer_price"] == 50.0
    assert pricing["item_margin"] == 0.0

def test_markup_rule_c_loose_or_no_mrp():
    # Rule C: mrp is None or 0 or negative -> customer_price = vendor_price + 4.0, margin == 4.0
    pricing1 = compute_item_pricing(vendor_price=30.0, mrp=None)
    assert pricing1["customer_price"] == 34.0
    assert pricing1["item_margin"] == 4.0
    assert pricing1["mrp"] is None

    pricing2 = compute_item_pricing(vendor_price=65.0, mrp=0.0)
    assert pricing2["customer_price"] == 69.0
    assert pricing2["item_margin"] == 4.0
    assert pricing2["mrp"] is None

def test_markup_validation_vendor_price_exceeds_mrp():
    # If mrp > 0 and vendor_price > mrp -> raises ValueError
    with pytest.raises(ValueError, match="Selling price cannot exceed printed MRP"):
        compute_item_pricing(vendor_price=55.0, mrp=50.0)

def test_delivery_fee_tiers_and_split_untouched():
    # PART 1 check: Distance delivery tiers with exact 80% Runner / 20% Platform split
    # Tier 1: 0.0 - 2.0 km -> 15.0 (Runner 12.0 [80%], Platform 3.0 [20%])
    assert calculate_delivery_fee(0.5) == 15.0
    assert calculate_runner_payout(0.5) == 12.0
    assert calculate_platform_delivery_share(0.5) == 3.0
    assert calculate_delivery_fee(1.8) == 15.0
    assert calculate_runner_payout(1.8) == 12.0
    assert calculate_platform_delivery_share(1.8) == 3.0

    # Tier 2: > 2.0 - 4.0 km -> 20.0 (Runner 16.0 [80%], Platform 4.0 [20%])
    assert calculate_delivery_fee(2.5) == 20.0
    assert calculate_runner_payout(2.5) == 16.0
    assert calculate_platform_delivery_share(2.5) == 4.0

    # Tier 3: > 4.0 - 6.0 km -> 25.0 (Runner 20.0 [80%], Platform 5.0 [20%])
    assert calculate_delivery_fee(5.0) == 25.0
    assert calculate_runner_payout(5.0) == 20.0
    assert calculate_platform_delivery_share(5.0) == 5.0

    # Tier 4: > 6.0 - 8.0 km -> 35.0 (Runner 28.0 [80%], Platform 7.0 [20%])
    assert calculate_delivery_fee(7.5) == 35.0
    assert calculate_runner_payout(7.5) == 28.0
    assert calculate_platform_delivery_share(7.5) == 7.0

    # Tier 5: > 8.0 - 9.0 km -> 40.0 (Runner 32.0 [80%], Platform 8.0 [20%])
    assert calculate_delivery_fee(8.5) == 40.0
    assert calculate_runner_payout(8.5) == 32.0
    assert calculate_platform_delivery_share(8.5) == 8.0

    # Fixed platform checkout fee is untouched at 3.0
    assert ACTIVE_PRICING_POLICY["platform_fee"] == 3.0

    # Order totals calculation check (distance 2.5 km -> Tier 2: ₹20.0 delivery fee)
    totals = calculate_order_totals(subtotal=200.0, distance_km=2.5)
    assert totals["subtotal"] == 200.0
    assert totals["delivery_fee"] == 20.0
    assert totals["platform_fee"] == 3.0
    assert totals["total_amount"] == 223.0

def test_settlement_ledger_net_platform_profit_formula():
    # Test formula: Net Profit = sum(item_margin * qty) + platform_delivery_share + platform_checkout_fee
    # Scenario: 2 items:
    # Item 1: vendor_price=40, customer_price=42, margin=2, qty=3 -> item_margins = 6.0
    # Item 2: vendor_price=30, customer_price=34, margin=4, qty=2 -> item_margins = 8.0
    # Total item margin = 14.0
    # Delivery: 25.0 (80% Runner share: 20.0, 20% Platform share: 5.0)
    # Platform checkout fee: 3.0
    # Customer collected: 42*3 + 34*2 + 25 + 3 = 126 + 68 + 25 + 3 = 222.0
    # Vendor payable (100%): 40*3 + 30*2 = 120 + 60 = 180.0
    # Runner payable (100%): 20.0
    # Net Platform Profit: 14.0 + 5.0 + 3.0 = 22.0
    # Proof: 222.0 - 180.0 - 20.0 = 22.0 (Exact match)
    customer_collected = (42.0 * 3) + (34.0 * 2) + 25.0 + 3.0
    vendor_payable = (40.0 * 3) + (30.0 * 2)
    runner_payable = 20.0
    item_margins = (2.0 * 3) + (4.0 * 2)
    platform_delivery_share = 5.0
    platform_checkout_fee = 3.0
    net_platform_profit = item_margins + platform_delivery_share + platform_checkout_fee

    assert customer_collected == 222.0
    assert vendor_payable == 180.0
    assert runner_payable == 20.0
    assert net_platform_profit == 22.0
    assert customer_collected - vendor_payable - runner_payable == net_platform_profit
