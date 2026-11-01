import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import async_engine, AsyncSessionLocal
from app.models.base import Base, User, Store, StoreProduct, GlobalCatalogItem, Runner, Address
from app.api.v1 import auth, addresses, stores, orders, ai, admin, support

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Seed pilot data for Minapur Block, Muzaffarpur, Bihar
    async with AsyncSessionLocal() as session:
        # 1. Global catalog items
        cat_check = await session.execute(select(GlobalCatalogItem))
        if not cat_check.scalars().first():
            items = [
                GlobalCatalogItem(
                    id="cat_atta",
                    name_en="Chakki Fresh Atta",
                    name_hi="ताज़ा चक्की आटा",
                    category="Grocery",
                    default_unit="1 kg",
                    suggested_mrp=45.0,
                    image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400",
                    tags="atta,aata,wheat,flour,आटा"
                ),
                GlobalCatalogItem(
                    id="cat_rice",
                    name_en="Basmati Rice (Minapur Special)",
                    name_hi="बासमती चावल",
                    category="Grocery",
                    default_unit="1 kg",
                    suggested_mrp=65.0,
                    image_url="https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400",
                    tags="rice,chawal,चावल"
                ),
                GlobalCatalogItem(
                    id="cat_mustard_oil",
                    name_en="Kachhi Ghani Mustard Oil",
                    name_hi="कच्ची घानी सरसों तेल",
                    category="Grocery",
                    default_unit="1 L",
                    suggested_mrp=155.0,
                    image_url="https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400",
                    tags="oil,mustard,tel,सरसों तेल"
                ),
                GlobalCatalogItem(
                    id="cat_milk",
                    name_en="Fresh Cow Milk",
                    name_hi="ताज़ा गाय का दूध",
                    category="Dairy",
                    default_unit="1 L",
                    suggested_mrp=60.0,
                    image_url="https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400",
                    tags="milk,doodh,dairy,दूध"
                ),
                GlobalCatalogItem(
                    id="cat_potato",
                    name_en="Fresh Local Potato (Aloo)",
                    name_hi="ताज़ा देशी आलू",
                    category="Vegetables",
                    default_unit="1 kg",
                    suggested_mrp=30.0,
                    image_url="https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400",
                    tags="potato,aloo,आलू"
                ),
                GlobalCatalogItem(
                    id="cat_onion",
                    name_en="Red Onion (Pyaz)",
                    name_hi="लाल प्याज़",
                    category="Vegetables",
                    default_unit="1 kg",
                    suggested_mrp=40.0,
                    image_url="https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400",
                    tags="onion,pyaz,प्याज"
                ),
                GlobalCatalogItem(
                    id="cat_tomato",
                    name_en="Desi Tomato (Tamatar)",
                    name_hi="देशी लाल टमाटर",
                    category="Vegetables",
                    default_unit="1 kg",
                    suggested_mrp=35.0,
                    image_url="https://images.unsplash.com/photo-1546470427-227c7369a941?w=400",
                    tags="tomato,tamatar,टमाटर"
                ),
                GlobalCatalogItem(
                    id="cat_pooja_agarbatti",
                    name_en="Chandan Agarbatti Incense",
                    name_hi="चंदन अगरबत्ती",
                    category="Pooja",
                    default_unit="1 pack",
                    suggested_mrp=25.0,
                    image_url="https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400",
                    tags="agarbatti,pooja,अगरबत्ती"
                ),
                GlobalCatalogItem(
                    id="cat_led_bulb",
                    name_en="9W LED Energy Saver Bulb",
                    name_hi="९ वॉट एलईडी बल्ब",
                    category="Electrical",
                    default_unit="1 piece",
                    suggested_mrp=99.0,
                    image_url="https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=400",
                    tags="bulb,led,light,बल्ब"
                ),
                GlobalCatalogItem(
                    id="cat_sugar",
                    name_en="Pure Refined Sugar (Cheeni)",
                    name_hi="सफ़ेद चीनी (शक्कर)",
                    category="Grocery",
                    default_unit="1 kg",
                    suggested_mrp=46.0,
                    image_url="https://images.unsplash.com/photo-1622484212850-eb596d769edc?w=400",
                    tags="sugar,cheeni,shakkar,चीनी"
                ),
                GlobalCatalogItem(
                    id="cat_salt",
                    name_en="Tata Iodized Salt (Namak)",
                    name_hi="आयोडीन युक्त नमक",
                    category="Grocery",
                    default_unit="1 kg",
                    suggested_mrp=28.0,
                    image_url="https://images.unsplash.com/photo-1626082896492-766af4eb6501?w=400",
                    tags="salt,namak,नमक"
                ),
                GlobalCatalogItem(
                    id="cat_biscuits",
                    name_en="Parle-G Glucose Biscuits",
                    name_hi="पारले-जी ग्लूकोज बिस्कुट",
                    category="Snacks",
                    default_unit="1 pack (250g)",
                    suggested_mrp=25.0,
                    image_url="https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400",
                    tags="biscuit,parle,snacks,बिस्कुट"
                ),
                GlobalCatalogItem(
                    id="cat_green_chili",
                    name_en="Fresh Green Chili & Coriander Combo",
                    name_hi="ताज़ा हरी मिर्च और धनिया",
                    category="Vegetables",
                    default_unit="250 g",
                    suggested_mrp=20.0,
                    image_url="https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=400",
                    tags="chili,coriander,mirchi,dhaniya,मिर्च"
                ),
                GlobalCatalogItem(
                    id="cat_toor_dal",
                    name_en="Desi Toor / Arhar Dal",
                    name_hi="देशी अरहर (तुअर) दाल",
                    category="Grocery",
                    default_unit="1 kg",
                    suggested_mrp=145.0,
                    image_url="https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=400",
                    tags="dal,toor,arhar,दाल"
                )
            ]
            session.add_all(items)
            await session.commit()
            
        # 2. Pilot Stores in Minapur
        store_check = await session.execute(select(Store))
        if not store_check.scalars().first():
            # Vendor 1 User
            u_v1 = User(id="usr_v1", phone="9800000001", name="Raju Sharma", role="vendor", preferred_language="hi")
            session.add(u_v1)
            await session.flush()
            
            # Store 1: Featured 1 (Chaturshi)
            st1 = Store(
                id="str_01",
                owner_id=u_v1.id,
                shop_name="माँ शारदा किराना स्टोर (Maa Sharda Kirana)",
                owner_name="Raju Sharma",
                category="Grocery",
                latitude=26.2230,
                longitude=85.3520,
                village="Chaturshi / Chatursi",
                landmark="Near Gram Panchayat Bhavan",
                block="Minapur",
                district="Muzaffarpur",
                is_online=True,
                is_approved=True,
                is_featured=True,
                rating=4.9,
                banner_url="https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=500"
            )
            session.add(st1)
            
            # Vendor 2 User
            u_v2 = User(id="usr_v2", phone="9800000002", name="Mukesh Prasad", role="vendor", preferred_language="hi")
            session.add(u_v2)
            await session.flush()
            
            # Store 2: Featured 2 (Tubanaghara / Benaghara)
            st2 = Store(
                id="str_02",
                owner_id=u_v2.id,
                shop_name="बजरंग जनरल एवं डेयरी (Bajrang Store)",
                owner_name="Mukesh Prasad",
                category="Dairy & Grocery",
                latitude=26.2080,
                longitude=85.3370,
                village="Tubanaghara / Benaghara",
                landmark="Near Middle School Chowk",
                block="Minapur",
                district="Muzaffarpur",
                is_online=True,
                is_approved=True,
                is_featured=True,
                rating=4.8,
                banner_url="https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=500"
            )
            session.add(st2)
            await session.commit()
            
            # Products for Store 1
            st1_products = [
                StoreProduct(store_id="str_01", global_product_id="cat_atta", category="Grocery", unit="1 kg", price=38.0, mrp=45.0, image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400"),
                StoreProduct(store_id="str_01", global_product_id="cat_rice", category="Grocery", unit="1 kg", price=54.0, mrp=65.0, image_url="https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400"),
                StoreProduct(store_id="str_01", global_product_id="cat_mustard_oil", category="Grocery", unit="1 L", price=142.0, mrp=155.0, image_url="https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400"),
                StoreProduct(store_id="str_01", global_product_id="cat_potato", category="Vegetables", unit="1 kg", price=24.0, mrp=30.0, image_url="https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400"),
                StoreProduct(store_id="str_01", global_product_id="cat_onion", category="Vegetables", unit="1 kg", price=32.0, mrp=40.0, image_url="https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400"),
                StoreProduct(store_id="str_01", global_product_id="cat_pooja_agarbatti", category="Pooja", unit="1 pack", price=20.0, mrp=25.0, image_url="https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400"),
                StoreProduct(store_id="str_01", global_product_id="cat_led_bulb", category="Electrical", unit="1 piece", price=85.0, mrp=99.0, image_url="https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=400"),
            ]
            session.add_all(st1_products)
            
            # Products for Store 2
            st2_products = [
                StoreProduct(store_id="str_02", global_product_id="cat_milk", category="Dairy", unit="1 L", price=56.0, mrp=60.0, image_url="https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400"),
                StoreProduct(store_id="str_02", global_product_id="cat_potato", category="Vegetables", unit="1 kg", price=25.0, mrp=30.0, image_url="https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400"),
                StoreProduct(store_id="str_02", global_product_id="cat_tomato", category="Vegetables", unit="1 kg", price=28.0, mrp=35.0, image_url="https://images.unsplash.com/photo-1546470427-227c7369a941?w=400"),
                StoreProduct(store_id="str_02", global_product_id="cat_atta", category="Grocery", unit="1 kg", price=39.0, mrp=45.0, image_url="https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400"),
            ]
            session.add_all(st2_products)
            
            # 3. Pilot Runner
            u_r = User(id="usr_r1", phone="9800000003", name="Santosh Kumar", role="runner", preferred_language="hi")
            session.add(u_r)
            await session.flush()
            
            runner = Runner(
                id="run_01",
                user_id=u_r.id,
                full_name="Santosh Kumar",
                vehicle_type="Motorcycle",
                vehicle_number="BR-06-AB-1234",
                driving_licence_no="DL-062024009876",
                is_online=True,
                is_approved=True,
                current_latitude=26.2230,
                current_longitude=85.3520
            )
            session.add(runner)
            
            # 4. Pilot Customer (Test Persona 9800000000)
            u_c0 = User(id="usr_c0", phone="9800000000", name="Ramesh Singh", role="customer", preferred_language="hi")
            session.add(u_c0)
            await session.flush()
            
            addr0 = Address(
                id="addr_c0",
                user_id=u_c0.id,
                title="Home",
                recipient_name="Ramesh Singh",
                phone="9800000000",
                latitude=26.2210,
                longitude=85.3500,
                village="Chaturshi",
                landmark="Near Shiv Mandir",
                block="Minapur",
                district="Muzaffarpur",
                state="Bihar",
                is_default=True
            )
            session.add(addr0)

            # Pilot Customer 2
            u_c = User(id="usr_c1", phone="9876543210", name="Ramesh Singh", role="customer", preferred_language="hi")
            session.add(u_c)
            await session.flush()
            
            addr = Address(
                id="addr_c1",
                user_id=u_c.id,
                title="Home",
                recipient_name="Ramesh Singh",
                phone="9876543210",
                latitude=26.2210,
                longitude=85.3500,
                village="Chaturshi",
                landmark="Near Shiv Mandir",
                block="Minapur",
                district="Muzaffarpur",
                state="Bihar",
                is_default=True
            )
            session.add(addr)

            # 5. Super Admin (Test Persona 9800000099)
            u_admin = User(
                id="usr_admin_01",
                phone="9800000099",
                name="GaonBazaar Super Admin",
                role="admin",
                preferred_language="en",
                is_active=True
            )
            session.add(u_admin)
            
            await session.commit()
            
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach API routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(addresses.router, prefix=settings.API_V1_STR)
app.include_router(stores.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(support.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "pilot_location": f"{settings.PILOT_BLOCK}, {settings.PILOT_DISTRICT}, {settings.PILOT_STATE}",
        "max_delivery_radius_km": settings.MAX_DELIVERY_RADIUS_KM,
        "platform_fee": settings.PLATFORM_FEE,
        "cancel_window_seconds": settings.CUSTOMER_CANCEL_WINDOW_SECONDS,
        "docs_url": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "commit": os.getenv("RENDER_GIT_COMMIT", "c30afc3")
    }
