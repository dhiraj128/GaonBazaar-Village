import math
from typing import Tuple, Optional
from app.core.config import settings

# Pilot Localities in Minapur Block, Muzaffarpur, Bihar
PILOT_LOCALITIES = [
    {
        "name": "Chaturshi / Chatursi",
        "latitude": 26.2230,
        "longitude": 85.3520,
        "block": "Minapur",
        "district": "Muzaffarpur",
        "landmark": "Near Gram Panchayat Bhavan"
    },
    {
        "name": "Tubanaghara / Benaghara",
        "latitude": 26.2080,
        "longitude": 85.3370,
        "block": "Minapur",
        "district": "Muzaffarpur",
        "landmark": "Near Middle School"
    },
    {
        "name": "Sivay Patti",
        "latitude": 26.2310,
        "longitude": 85.3610,
        "block": "Minapur",
        "district": "Muzaffarpur",
        "landmark": "Near Shiv Mandir Chowk"
    },
    {
        "name": "Tulsi Ganj / Bangaon",
        "latitude": 26.1980,
        "longitude": 85.3420,
        "block": "Minapur",
        "district": "Muzaffarpur",
        "landmark": "Near Market Chowk"
    }
]

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees) using Haversine formula.
    """
    R = 6371.0 # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = R * c
    return round(distance, 2)

def is_within_service_radius(store_lat: float, store_lon: float, customer_lat: float, customer_lon: float) -> Tuple[bool, float]:
    """
    Strictly verifies if distance is <= 8.0 km.
    Returns (is_serviceable, distance_km).
    """
    dist = calculate_haversine_distance(store_lat, store_lon, customer_lat, customer_lon)
    return dist <= settings.MAX_DELIVERY_RADIUS_KM, dist

def get_nearest_pilot_locality(lat: float, lon: float) -> Tuple[Optional[dict], float]:
    """
    Finds the closest known pilot locality in Minapur block.
    """
    closest_loc = None
    min_dist = float("inf")
    for loc in PILOT_LOCALITIES:
        dist = calculate_haversine_distance(lat, lon, loc["latitude"], loc["longitude"])
        if dist < min_dist:
            min_dist = dist
            closest_loc = loc
    return closest_loc, min_dist
