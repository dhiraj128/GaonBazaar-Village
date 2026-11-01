from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "GaonBazaar Rural Hyperlocal Delivery API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "gaonbazaar-super-secret-rural-hyperlocal-key-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database (Default to SQLite file for robust local testing without external daemon)
    DATABASE_URL: str = "sqlite+aiosqlite:///./gaonbazaar.db"
    SYNC_DATABASE_URL: str = "sqlite:///./gaonbazaar.db"
    
    # Rural Hyperlocal Configuration
    MAX_DELIVERY_RADIUS_KM: float = 8.0
    BASE_DELIVERY_FEE: float = 15.0
    PER_KM_DELIVERY_FEE: float = 5.0
    PLATFORM_FEE: float = 3.0 # Strict ₹3 platform fee
    CUSTOMER_CANCEL_WINDOW_SECONDS: int = 180 # Strict 180-second cancellation
    
    # Pilot Geography: Minapur Block, Muzaffarpur, Bihar
    PILOT_BLOCK: str = "Minapur"
    PILOT_DISTRICT: str = "Muzaffarpur"
    PILOT_STATE: str = "Bihar"
    DEFAULT_CENTER_LAT: float = 26.2153
    DEFAULT_CENTER_LNG: float = 85.3456
    
    class Config:
        case_sensitive = True

settings = Settings()
