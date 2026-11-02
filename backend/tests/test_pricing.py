import pytest
from app.services.pricing_service import calculate_delivery_fee, calculate_order_totals
from app.core.config import settings

def test_delivery_fee_tiering():
    # 0 - 2 km -> ₹15.0
    assert calculate_delivery_fee(1.5) == 15.0
    assert calculate_delivery_fee(2.0) == 15.0
    
    # > 2 - 4 km -> ₹20.0
    assert calculate_delivery_fee(2.5) == 20.0
    assert calculate_delivery_fee(4.0) == 20.0
    
    # > 4 - 5 km -> ₹25.0
    assert calculate_delivery_fee(4.5) == 25.0
    assert calculate_delivery_fee(5.0) == 25.0
    
    # > 5 - 8 km -> ₹35.0
    assert calculate_delivery_fee(6.0) == 35.0
    assert calculate_delivery_fee(8.0) == 35.0

def test_strict_platform_fee_and_totals():
    # Verify strict ₹3 platform fee
    assert settings.PLATFORM_FEE == 3.0
    
    subtotal = 200.0
    distance_km = 2.0 # ₹15 delivery fee
    totals = calculate_order_totals(subtotal, distance_km)
    
    assert totals["subtotal"] == 200.0
    assert totals["delivery_fee"] == 15.0
    assert totals["platform_fee"] == 3.0
    assert totals["total_amount"] == 218.0 # 200 + 15 + 3
