with open('backend/app/api/v1/orders.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_s = 'is_live = order.status in ["PICKED_UP", "OUT_FOR_DELIVERY"] and runner is not None'
new_s = 'is_live = order.status in ["ASSIGNED", "PICKED_UP", "OUT_FOR_DELIVERY"] and runner is not None'

assert old_s in content, 'old_s not found'
content = content.replace(old_s, new_s, 1)

with open('backend/app/api/v1/orders.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated track_order is_live logic in orders.py')
