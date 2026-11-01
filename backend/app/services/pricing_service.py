from app.core.config import settings

def calculate_delivery_fee(distance_km: float) -> float:
    """
    Tiered delivery fee calculation:
    - Base fee: ₹15.0 for first 3.0 km
    - Thereafter: ₹5.0 per additional km
    """
    if distance_km <= 3.0:
        return settings.BASE_DELIVERY_FEE
    additional_km = distance_km - 3.0
    return round(settings.BASE_DELIVERY_FEE + (additional_km * settings.PER_KM_DELIVERY_FEE), 2)

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
