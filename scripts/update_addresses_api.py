with open('backend/app/api/v1/addresses.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    'from app.schemas.address import (\n    AddressCreate, AddressResponse, ServiceabilityCheckRequest, ServiceabilityCheckResponse\n)',
    'from app.schemas.address import (\n    AddressCreate, AddressUpdate, AddressResponse, ServiceabilityCheckRequest, ServiceabilityCheckResponse\n)'
)
if 'AddressUpdate' not in content:
    # Try with CRLF
    content = content.replace(
        'from app.schemas.address import (\r\n    AddressCreate, AddressResponse, ServiceabilityCheckRequest, ServiceabilityCheckResponse\r\n)',
        'from app.schemas.address import (\r\n    AddressCreate, AddressUpdate, AddressResponse, ServiceabilityCheckRequest, ServiceabilityCheckResponse\r\n)'
    )

new_routes = '''
@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    data: AddressUpdate,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    result = await db.execute(
        select(Address).where(Address.id == address_id, Address.user_id == user_id)
    )
    address = result.scalars().first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    if data.is_default:
        all_res = await db.execute(select(Address).where(Address.user_id == user_id))
        for existing in all_res.scalars().all():
            existing.is_default = False

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(address, field, val)

    await db.commit()
    await db.refresh(address)

    return AddressResponse(
        id=address.id,
        user_id=address.user_id,
        title=address.title,
        recipient_name=address.recipient_name,
        phone=address.phone,
        latitude=address.latitude,
        longitude=address.longitude,
        village=address.village,
        landmark=address.landmark,
        block=address.block,
        district=address.district,
        state=address.state,
        is_default=address.is_default
    )

@router.patch("/{address_id}/default", response_model=AddressResponse)
async def set_default_address(
    address_id: str,
    payload: dict = Depends(get_current_user_payload),
    db: AsyncSession = Depends(get_db)
):
    user_id = payload.get("sub")
    all_res = await db.execute(select(Address).where(Address.user_id == user_id))
    all_addrs = all_res.scalars().all()
    target = None
    for a in all_addrs:
        if a.id == address_id:
            a.is_default = True
            target = a
        else:
            a.is_default = False

    if not target:
        raise HTTPException(status_code=404, detail="Address not found")

    await db.commit()
    await db.refresh(target)

    return AddressResponse(
        id=target.id,
        user_id=target.user_id,
        title=target.title,
        recipient_name=target.recipient_name,
        phone=target.phone,
        latitude=target.latitude,
        longitude=target.longitude,
        village=target.village,
        landmark=target.landmark,
        block=target.block,
        district=target.district,
        state=target.state,
        is_default=target.is_default
    )
'''

# Insert before @router.delete
if '@router.put("/{address_id}"' not in content:
    content = content.replace('@router.delete("/{address_id}"', new_routes.strip() + '\n\n@router.delete("/{address_id}"')

with open('backend/app/api/v1/addresses.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated addresses.py with PUT and PATCH default endpoints')
