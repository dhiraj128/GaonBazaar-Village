from app.core.config import settings
from typing import Dict, Any, List

# Proposed 5-tier delivery pricing matrix (Part 4.7)
# Rates in INR Rupees and deterministic Integer-Paise
DEFAULT_PRICING_TIERS = [
    {
        "min_km": 0.0,
        "max_km": 1.0,
        "customer_fee": 15.0,
        "customer_fee_paise": 1500,
        "runner_payout": 10.0,
        "runner_payout_paise": 1000,
        "platform_share": 5.0,
        "platform_share_paise": 500,
    },
    {
        "min_km": 1.0,
        "max_km": 2.0,
        "customer_fee": 20.0,
        "customer_fee_paise": 2000,
        "runner_payout": 14.0,
        "runner_payout_paise": 1400,
        "platform_share": 6.0,
        "platform_share_paise": 600,
    },
    {
        "min_km": 2.0,
        "max_km": 4.0,
        "customer_fee": 25.0,
        "customer_fee_paise": 2500,
        "runner_payout": 18.0,
        "runner_payout_paise": 1800,
        "platform_share": 7.0,
        "platform_share_paise": 700,
    },
    {
        "min_km": 4.0,
        "max_km": 6.0,
        "customer_fee": 30.0,
        "customer_fee_paise": 3000,
        "runner_payout": 22.0,
        "runner_payout_paise": 2200,
        "platform_share": 8.0,
        "platform_share_paise": 800,
    },
    {
        "min_km": 6.0,
        "max_km": 8.0,
        "customer_fee": 40.0,
        "customer_fee_paise": 4000,
        "runner_payout": 28.0,
        "runner_payout_paise": 2800,
        "platform_share": 12.0,
        "platform_share_paise": 1200,
    },
]

# Configurable in-memory active pricing policy (can be updated via Admin API)
ACTIVE_PRICING_POLICY = {
    "version": "v2_rural_5tier",
    "platform_fee": 3.0,
    "platform_fee_paise": 300,
    "max_geofence_km": 8.0,
    "tiers": DEFAULT_PRICING_TIERS
}

def get_tier_for_distance(distance_km: float) -> Dict[str, Any]:
    """Find the applicable pricing tier for a given distance in km."""
    for tier in ACTIVE_PRICING_POLICY["tiers"]:
        if tier["min_km"] == 0.0 and distance_km <= tier["max_km"]:
            return tier
        elif tier["min_km"] < distance_km <= tier["max_km"]:
            return tier
    # If beyond max tier or edge case, use highest tier within geofence
    return ACTIVE_PRICING_POLICY["tiers"][-1]

def calculate_delivery_fee(distance_km: float) -> float:
    """
    Returns the customer delivery fee in Rupees.
    Supports legacy 4-tier checks and proposed 5-tier pricing.
    """
    tier = get_tier_for_distance(distance_km)
    return float(tier["customer_fee"])

def calculate_delivery_fee_paise(distance_km: float) -> int:
    """Returns deterministic integer-paise customer delivery fee."""
    tier = get_tier_for_distance(distance_km)
    return int(tier["customer_fee_paise"])

def calculate_runner_payout(distance_km: float) -> float:
    """Returns the single-delivery runner payout in Rupees."""
    tier = get_tier_for_distance(distance_km)
    return float(tier["runner_payout"])

def calculate_runner_payout_paise(distance_km: float) -> int:
    """Returns deterministic integer-paise single-delivery runner payout."""
    tier = get_tier_for_distance(distance_km)
    return int(tier["runner_payout_paise"])

def calculate_platform_delivery_share(distance_km: float) -> float:
    """Returns the platform gross delivery share in Rupees."""
    tier = get_tier_for_distance(distance_km)
    return float(tier["platform_share"])

def calculate_batch_payout(num_orders: int, route_distance_km: float) -> Dict[str, Any]:
    """
    Multiple-Order Batch Payout Algorithm (Part 4.6):
    - Base store pickup compensation: ₹10 (1000 paise)
    - Per drop-off customer stop compensation: ₹8 (800 paise) per order
    - Route transit distance rate: ₹6 (600 paise) per km
    Returns total batch payout, breakdown, and integer paise.
    """
    base_pickup_paise = 1000
    drop_fee_paise = num_orders * 800
    distance_fee_paise = int(round(route_distance_km * 600))
    total_payout_paise = base_pickup_paise + drop_fee_paise + distance_fee_paise
    total_payout_rupees = round(total_payout_paise / 100.0, 2)
    
    return {
        "num_orders": num_orders,
        "route_distance_km": round(route_distance_km, 2),
        "base_pickup_rupees": 10.0,
        "drop_fees_rupees": round(drop_fee_paise / 100.0, 2),
        "distance_fee_rupees": round(distance_fee_paise / 100.0, 2),
        "total_payout_rupees": total_payout_rupees,
        "total_payout_paise": total_payout_paise,
    }

def calculate_order_totals(subtotal: float, distance_km: float) -> Dict[str, float]:
    """
    Calculates subtotal, delivery fee, platform fee (strict ₹3.00), and final amount.
    All computed with deterministic integer-paise arithmetic to eliminate floating-point drift.
    """
    subtotal_paise = int(round(subtotal * 100))
    delivery_fee_paise = calculate_delivery_fee_paise(distance_km)
    platform_fee_paise = int(round(ACTIVE_PRICING_POLICY["platform_fee"] * 100))
    total_amount_paise = subtotal_paise + delivery_fee_paise + platform_fee_paise

    return {
        "subtotal": round(subtotal_paise / 100.0, 2),
        "delivery_fee": round(delivery_fee_paise / 100.0, 2),
        "platform_fee": round(platform_fee_paise / 100.0, 2),
        "total_amount": round(total_amount_paise / 100.0, 2)
    }
