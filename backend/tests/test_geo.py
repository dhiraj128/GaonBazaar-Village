import pytest
from app.services.geo_service import (
    calculate_haversine_distance, is_within_service_radius, get_nearest_pilot_locality
)
from app.core.config import settings

def test_haversine_distance_calculation():
    # Minapur center to Chaturshi (~1.0 km)
    dist = calculate_haversine_distance(26.2153, 85.3456, 26.2230, 85.3520)
    assert 0.5 < dist < 2.0

def test_service_radius_enforcement():
    # Inside 8 km policy
    is_serv, dist = is_within_service_radius(26.2230, 85.3520, 26.2080, 85.3370)
    assert is_serv is True
    assert dist <= settings.MAX_DELIVERY_RADIUS_KM
    
    # Outside 8 km policy (e.g. Patna or Muzaffarpur town center 25 km away)
    is_serv_far, dist_far = is_within_service_radius(26.2230, 85.3520, 26.1200, 85.3900)
    assert is_serv_far is False
    assert dist_far > 8.0

def test_nearest_pilot_locality():
    loc, dist = get_nearest_pilot_locality(26.2230, 85.3520)
    assert loc is not None
    assert "Chaturshi" in loc["name"]
    assert dist < 0.1
