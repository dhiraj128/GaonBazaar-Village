with open('backend/app/api/v1/ration_lists.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_block = '''    # Load store products if store exists
    store_products = {}
    if target_store:
        sp_res = await db.execute(select(StoreProduct).where(StoreProduct.store_id == target_store.id))
        for sp in sp_res.scalars().all():
            if sp.global_product_id:
                store_products[sp.global_product_id] = sp
            store_products[sp.name_en.lower()] = sp

    # Load global catalog as backup reference
    gc_res = await db.execute(select(GlobalCatalogItem))
    catalog_map = {item.id: item for item in gc_res.scalars().all()}'''

new_block = '''    # Load global catalog as reference
    gc_res = await db.execute(select(GlobalCatalogItem))
    catalog_map = {item.id: item for item in gc_res.scalars().all()}

    # Load store products if store exists
    store_products = {}
    if target_store:
        sp_res = await db.execute(select(StoreProduct).where(StoreProduct.store_id == target_store.id))
        for sp in sp_res.scalars().all():
            if sp.global_product_id:
                store_products[sp.global_product_id] = sp
            p_name = sp.custom_name_en or (catalog_map[sp.global_product_id].name_en if sp.global_product_id in catalog_map else "")
            if p_name:
                store_products[p_name.lower()] = sp'''

assert old_block in content, 'old_block not found'
content = content.replace(old_block, new_block)

with open('backend/app/api/v1/ration_lists.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated store_products mapping in ration_lists.py')
