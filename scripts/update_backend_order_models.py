"""
Update Order model, schema, and API for 3-way order routing pipeline.
"""
import os

def update_model():
    path = "backend/app/models/base.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    target = '    customer_id = Column(String(36), ForeignKey("users.id"), nullable=False)\n    store_id = Column(String(36), ForeignKey("stores.id"), nullable=False)\n    runner_id = Column(String(36), ForeignKey("runners.id"), nullable=True)\n    delivery_address_id = Column(String(36), ForeignKey("addresses.id"), nullable=False)'
    
    replacement = '    order_id = Column(String(36), default=generate_uuid, index=True)\n    customer_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)\n    store_id = Column(String(36), ForeignKey("stores.id"), nullable=False)\n    vendor_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)\n    runner_id = Column(String(36), ForeignKey("runners.id"), nullable=True, index=True)\n    delivery_village = Column(String(100), nullable=True, index=True)\n    delivery_address_id = Column(String(36), ForeignKey("addresses.id"), nullable=False)'
    
    if target in content:
        content = content.replace(target, replacement, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated models/base.py")
    else:
        print("Target already updated or not found in models/base.py")

def update_schema():
    path = "backend/app/schemas/order.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = 'class OrderResponse(BaseModel):\n    id: str\n    customer_id: str'
    replacement = 'class OrderResponse(BaseModel):\n    id: str\n    order_id: Optional[str] = None\n    customer_id: str\n    vendor_id: Optional[str] = None\n    delivery_village: Optional[str] = None'

    if target in content:
        content = content.replace(target, replacement, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated schemas/order.py")
    else:
        print("Target already updated or not found in schemas/order.py")

def update_api():
    path = "backend/app/api/v1/orders.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update order creation to set order_id, vendor_id, delivery_village
    old_create = '''    order = Order(
        customer_id=customer_id,
        store_id=store.id,
        delivery_address_id=address.id,
        status="PLACED",'''

    new_create = '''    order = Order(
        customer_id=customer_id,
        vendor_id=store.owner_id if store else None,
        delivery_village=address.village if address else None,
        store_id=store.id,
        delivery_address_id=address.id,
        status="PENDING",'''

    if old_create in content:
        content = content.replace(old_create, new_create, 1)
        print("Updated create_order in api/v1/orders.py")

    # Ensure order.order_id = order.id before commit
    old_flush = '''    db.add(order)
    await db.flush()'''
    new_flush = '''    db.add(order)
    await db.flush()
    if not order.order_id:
        order.order_id = order.id'''

    if old_flush in content:
        content = content.replace(old_flush, new_flush, 1)
        print("Updated flush in api/v1/orders.py")

    # 2. Update vendor_order_action to accept PREPARING and READY_FOR_PICKUP
    old_act_accept = '''    if act == "ACCEPT":
        if order.status != "PLACED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot ACCEPT order in status \'{order.status}\'. Order must be \'PLACED\'.")
        order.status = "ACCEPTED"
        title = "दुकानदार ने स्वीकार किया (Accepted)"
    elif act in ["PACK", "PACKED"]:
        if order.status not in ["ACCEPTED", "PLACED"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot PACK order in status \'{order.status}\'. Order must be \'ACCEPTED\' or \'PLACED\'.")
        order.status = "PACKED"'''

    new_act_accept = '''    if act in ["ACCEPT", "PREPARING", "PREPARE"]:
        if order.status not in ["PLACED", "PENDING"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot ACCEPT order in status \'{order.status}\'. Order must be \'PENDING\' or \'PLACED\'.")
        order.status = "PREPARING"
        title = "दुकानदार ने स्वीकार किया (Accepted & Preparing)"
    elif act in ["PACK", "PACKED", "READY_FOR_PICKUP"]:
        if order.status not in ["ACCEPTED", "PREPARING", "PLACED", "PENDING"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot PACK order in status \'{order.status}\'.")
        order.status = "READY_FOR_PICKUP"'''

    if old_act_accept in content:
        content = content.replace(old_act_accept, new_act_accept, 1)
        print("Updated vendor_order_action in api/v1/orders.py")

    # 3. Update runner_job_action to support READY_FOR_PICKUP, RUNNER_ASSIGNED, OUT_FOR_DELIVERY
    old_runner_accept = '''        stmt_accept = (
            update(Order)
            .where(
                Order.id == order.id,
                Order.status.in_(["PACKED", "ACCEPTED"]),
                (Order.runner_id.is_(None) | (Order.runner_id == target_runner_id))
            )'''

    new_runner_accept = '''        stmt_accept = (
            update(Order)
            .where(
                Order.id == order.id,
                Order.status.in_(["READY_FOR_PICKUP", "PACKED", "ACCEPTED", "PREPARING"]),
                (Order.runner_id.is_(None) | (Order.runner_id == target_runner_id))
            )'''

    if old_runner_accept in content:
        content = content.replace(old_runner_accept, new_runner_accept, 1)
        print("Updated runner accept query in api/v1/orders.py")

    # 4. In _format_order_response, add order_id, vendor_id, delivery_village
    old_format = '''    return OrderResponse(
        id=order.id,
        customer_id=order.customer_id,'''

    new_format = '''    return OrderResponse(
        id=order.id,
        order_id=getattr(order, "order_id", None) or order.id,
        customer_id=order.customer_id,
        vendor_id=getattr(order, "vendor_id", None) or (order.store.owner_id if order.store else None),
        delivery_village=getattr(order, "delivery_village", None) or (order.delivery_address.village if order.delivery_address else None),'''

    if old_format in content:
        content = content.replace(old_format, new_format, 1)
        print("Updated _format_order_response in api/v1/orders.py")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_model()
    update_schema()
    update_api()
