import os

path = "backend/app/api/v1/stores.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_fn = """@router.get("/catalog/global", response_model=List[GlobalCatalogResponse])
async def get_global_catalog(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GlobalCatalogItem))
    items = result.scalars().all()
    return [
        GlobalCatalogResponse(
            id=i.id,
            name_en=i.name_en,
            name_hi=i.name_hi,
            category=i.category,
            default_unit=i.default_unit,
            suggested_mrp=i.suggested_mrp,
            image_url=i.image_url,
            tags=i.tags
        )
        for i in items
    ]"""

new_fn = """@router.get("/catalog/global", response_model=List[GlobalCatalogResponse])
async def get_global_catalog(
    query: Optional[str] = Query(None, description="Optional search query for dynamic FMCG catalog filtering"),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(GlobalCatalogItem)
    if query and query.strip():
        q_term = f"%{query.strip()}%"
        stmt = stmt.where(
            or_(
                GlobalCatalogItem.name_en.ilike(q_term),
                GlobalCatalogItem.name_hi.ilike(q_term),
                GlobalCatalogItem.category.ilike(q_term),
                GlobalCatalogItem.tags.ilike(q_term),
                GlobalCatalogItem.id.ilike(q_term)
            )
        )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return [
        GlobalCatalogResponse(
            id=i.id,
            name_en=i.name_en,
            name_hi=i.name_hi,
            category=i.category,
            default_unit=i.default_unit,
            suggested_mrp=i.suggested_mrp,
            image_url=i.image_url,
            tags=i.tags
        )
        for i in items
    ]"""

content_norm = content.replace("\r\n", "\n")
if old_fn in content_norm:
    content_norm = content_norm.replace(old_fn, new_fn, 1)
    with open(path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(content_norm)
    print("Updated get_global_catalog in stores.py successfully!")
else:
    print("Target not found in stores.py")
