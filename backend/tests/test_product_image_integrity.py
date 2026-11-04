import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

# Prohibited misleading image identifiers
PROHIBITED_IMAGE_FRAGMENTS = [
    "photo-1509440159596",  # Bread (prohibited for Atta/Flour)
    "photo-1515543237350",  # Aquarium fish (prohibited for Dal/Pulses)
    "photo-1626082896492",  # Rose flower (prohibited for Salt)
    "photo-1584308666744",  # Medical gloves (prohibited for Detergent)
    "photo-1599488615731",  # Cooked dal bowl (prohibited for raw Dal)
]

# Authoritative verified image assets for key staples
VERIFIED_IMAGE_STANDARDS = {
    "cat_atta": "photo-1574323347407",      # Raw wheat grain harvest
    "cat_salt": "photo-1518110903415",      # Pure culinary cooking salt
    "cat_toor_dal": "photo-1585994192701",  # Yellow split toor dal
    "cat_detergent": "photo-1585421514738", # Laundry washing detergent
}

@pytest.mark.asyncio
async def test_global_catalog_images_integrity():
    """Verify that every global catalog item has a verified image and no prohibited mismatched images exist."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/catalog/global")
        assert res.status_code == 200, f"Failed to fetch global catalog: {res.text}"
        items = res.json()
        assert len(items) > 0, "Global catalog must not be empty"

        for item in items:
            img = item.get("image_url") or ""
            assert img, f"Catalog item {item.get('id')} has missing image_url"
            
            # 1. Assert no prohibited image fragment is present
            for bad in PROHIBITED_IMAGE_FRAGMENTS:
                assert bad not in img, (
                    f"Product {item.get('id')} ({item.get('name_en')}) uses prohibited image fragment '{bad}': {img}"
                )

            # 2. Assert key staple items match authoritative verified standards
            item_id = item.get("id")
            if item_id in VERIFIED_IMAGE_STANDARDS:
                expected_fragment = VERIFIED_IMAGE_STANDARDS[item_id]
                assert expected_fragment in img, (
                    f"Product {item_id} ({item.get('name_en')}) image '{img}' does not match standard '{expected_fragment}'"
                )

@pytest.mark.asyncio
async def test_store_products_images_integrity():
    """Verify that store products populated from catalog do not contain prohibited images."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Check products of store 1 (Sharma Kirana)
        res = await client.get("/api/v1/stores/str_01/products")
        assert res.status_code == 200
        products = res.json()
        assert len(products) > 0

        for p in products:
            img = p.get("image_url") or ""
            for bad in PROHIBITED_IMAGE_FRAGMENTS:
                assert bad not in img, (
                    f"Store product {p.get('id')} ({p.get('name_en')}) contains prohibited image '{bad}': {img}"
                )
