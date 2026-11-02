from app.core.config import settings

def calculate_delivery_fee(distance_km: float) -> float:
    """
    Dynamic village delivery fee based on 8.0 km geofencing tiers:
    - 0 to 2 km: ₹15.0
    - > 2 to 4 km: ₹20.0
    - > 4 to 5 km: ₹25.0
    - > 5 to 8 km: ₹35.0
    """
    if distance_km <= 2.0:
        return 15.0
    elif distance_km <= 4.0:
        return 20.0
    elif distance_km <= 5.0:
        return 25.0
    else:
        return 35.0

def calculate_order_totals(subtotal: float, distance_km: float) -> dict:
    """
    Calculates subtotal, delivery fee, platform fee (strict ₹3.00), and final amount.
    """
    delivery_fee = calculate_delivery_fee(distance_km)
    platform_fee = settings.PLATFORM_FEE # Strict ₹3.00
    total_amount = round(subtotal + delivery_fee + platform_fee, 2)
    
    return {
        "subtotal": round(subtotal, 2),
        "delivery_fee": delivery_fee,
        "platform_fee": platform_fee,
        "total_amount": total_amount
    }
