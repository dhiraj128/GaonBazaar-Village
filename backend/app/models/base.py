from datetime import datetime, timezone
import uuid
from sqlalchemy import (
    Column, String, Boolean, Float, Integer, ForeignKey, DateTime, Text, Enum, Numeric, TypeDecorator
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid() -> str:
    return str(uuid.uuid4())

class UTCDateTime(TypeDecorator):
    """
    Ensures datetime objects are always stored and retrieved timezone-aware (UTC).
    Prevents 'can't subtract offset-naive and offset-aware datetimes' in asyncpg and SQLite.
    """
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if not isinstance(value, datetime):
                return value
            if value.tzinfo is None:
                utc_dt = value.replace(tzinfo=timezone.utc)
            else:
                utc_dt = value.astimezone(timezone.utc)
            # Store naive UTC representation in the database to completely prevent
            # asyncpg's Cython codec error: "can't subtract offset-naive and offset-aware datetimes"
            return utc_dt.replace(tzinfo=None)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, datetime):
                return value
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        return value

class OtpChallenge(Base):
    __tablename__ = "otp_challenges"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    phone = Column(String(15), index=True, nullable=False)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    otp_hash = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False, default="customer")
    attempts = Column(Integer, default=0)
    is_used = Column(Boolean, default=False)
    expires_at = Column(UTCDateTime, nullable=False)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    phone = Column(String(15), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=True)
    email = Column(String(120), nullable=True)
    role = Column(String(20), nullable=False, default="customer") # customer, vendor, runner, admin
    preferred_language = Column(String(5), default="hi") # hi or en
    avatar_url = Column(String(500), nullable=True)
    primary_village = Column(String(100), nullable=True)
    primary_panchayat = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", foreign_keys="[Order.customer_id]", back_populates="customer")
    store = relationship("Store", back_populates="owner", uselist=False)
    runner = relationship("Runner", back_populates="user", uselist=False)

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(50), default="Home") # Home, Shop, Other
    recipient_name = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    village = Column(String(100), nullable=False) # e.g. Chaturshi, Benaghara, Sivay Patti, Tulsi Ganj
    landmark = Column(String(150), nullable=True)
    block = Column(String(100), default="Minapur")
    district = Column(String(100), default="Muzaffarpur")
    state = Column(String(50), default="Bihar")
    is_default = Column(Boolean, default=False)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="addresses")

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    shop_name = Column(String(150), nullable=False)
    owner_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False) # Grocery, Vegetables, Dairy, Pooja, Hardware, General
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    village = Column(String(100), nullable=False)
    landmark = Column(String(150), nullable=True)
    block = Column(String(100), default="Minapur")
    district = Column(String(100), default="Muzaffarpur")
    is_online = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    rating = Column(Float, default=4.8)
    banner_url = Column(String(500), nullable=True)
    commission_rate = Column(Float, default=0.0) # Strict 0% introductory rate
    upi_id = Column(String(100), nullable=True)
    bank_account_info = Column(Text, nullable=True)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))
    
    owner = relationship("User", back_populates="store")
    products = relationship("StoreProduct", back_populates="store", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="store")

class Runner(Base):
    __tablename__ = "runners"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    vehicle_type = Column(String(30), default="Motorcycle") # Motorcycle, Bicycle
    vehicle_number = Column(String(30), nullable=True)
    driving_licence_no = Column(String(50), nullable=True)
    is_online = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    upi_id = Column(String(100), nullable=True)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="runner")
    orders = relationship("Order", back_populates="runner")

class GlobalCatalogItem(Base):
    __tablename__ = "global_catalog"
    
    id = Column(String(50), primary_key=True) # e.g. prd_atta_chakki
    name_en = Column(String(150), nullable=False)
    name_hi = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    default_unit = Column(String(30), nullable=False)
    suggested_mrp = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=False)
    tags = Column(String(200), nullable=True) # comma separated

class StoreProduct(Base):
    __tablename__ = "store_products"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    store_id = Column(String(36), ForeignKey("stores.id"), nullable=False)
    global_product_id = Column(String(50), ForeignKey("global_catalog.id"), nullable=True)
    custom_name_en = Column(String(150), nullable=True)
    custom_name_hi = Column(String(150), nullable=True)
    category = Column(String(50), nullable=False)
    unit = Column(String(30), nullable=False) # 1 kg, 500 g, 1 packet, etc.
    price = Column(Float, nullable=False)
    mrp = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=False)
    in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer, default=50)
    
    store = relationship("Store", back_populates="products")
    global_item = relationship("GlobalCatalogItem")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    store_id = Column(String(36), ForeignKey("stores.id"), nullable=False)
    runner_id = Column(String(36), ForeignKey("runners.id"), nullable=True)
    delivery_address_id = Column(String(36), ForeignKey("addresses.id"), nullable=False)
    
    # Status: PLACED -> ACCEPTED -> PACKED -> RUNNER_ASSIGNED -> PICKED_UP -> OUT_FOR_DELIVERY -> DELIVERED (or CANCELLED)
    status = Column(String(30), default="PLACED")
    subtotal = Column(Float, nullable=False)
    delivery_fee = Column(Float, nullable=False)
    platform_fee = Column(Float, default=3.0) # Strict ₹3 platform fee
    total_amount = Column(Float, nullable=False)
    
    payment_method = Column(String(20), default="COD") # COD, ONLINE
    payment_status = Column(String(20), default="PENDING") # PENDING, PAID, REFUNDED
    payment_order_id = Column(String(100), nullable=True) # Razorpay Order ID
    transaction_id = Column(String(100), nullable=True) # Razorpay Payment ID
    delivery_otp = Column(String(6), nullable=False) # 4 or 6 digit verification code
    
    placed_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))
    cancel_until = Column(UTCDateTime, nullable=False) # placed_at + 180s strict window
    delivered_at = Column(UTCDateTime, nullable=True)
    customer_notes = Column(Text, nullable=True)
    
    customer = relationship("User", foreign_keys=[customer_id], back_populates="orders")
    store = relationship("Store", back_populates="orders")
    runner = relationship("Runner", back_populates="orders")
    delivery_address = relationship("Address")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    timeline = relationship("OrderTimeline", back_populates="order", cascade="all, delete-orphan")
    messages = relationship("OrderMessage", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("store_products.id"), nullable=False)
    product_name_en = Column(String(150), nullable=False)
    product_name_hi = Column(String(150), nullable=False)
    unit = Column(String(30), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    
    order = relationship("Order", back_populates="items")
    product = relationship("StoreProduct")

class OrderTimeline(Base):
    __tablename__ = "order_timeline"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    status = Column(String(30), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    timestamp = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))
    
    order = relationship("Order", back_populates="timeline")

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=True)
    subject = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(30), default="OPEN") # OPEN, RESOLVED, CLOSED
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    actor_id = Column(String(36), nullable=True)
    actor_role = Column(String(20), default="admin")
    action = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))


class OrderMessage(Base):
    __tablename__ = "order_messages"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    sender_role = Column(String(20), nullable=False) # customer, runner, vendor, admin
    sender_name = Column(String(100), nullable=False)
    message_type = Column(String(30), nullable=False, default="TEXT") # TEXT, LOCATION_PIN, LIVE_LOCATION_START, LIVE_LOCATION_STOP
    content = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_title = Column(String(150), nullable=True)
    created_at = Column(UTCDateTime, default=lambda: datetime.now(timezone.utc))

    order = relationship("Order", back_populates="messages")
    sender = relationship("User")
