with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
if 'ration_lists' not in content:
    content = content.replace(
        'from app.models.base import Base, User, Store, StoreProduct, GlobalCatalogItem, Runner, Address, OrderMessage, Notification',
        'from app.models.base import Base, User, Store, StoreProduct, GlobalCatalogItem, Runner, Address, OrderMessage, Notification, MonthlyRationList, MonthlyRationItem'
    )
    content = content.replace(
        'from app.api.v1 import auth, addresses, stores, orders, ai, admin, support, payments, notifications',
        'from app.api.v1 import auth, addresses, stores, orders, ai, admin, support, payments, notifications, ration_lists'
    )

# 2. Add table creation migration statements
table_migrations = '''        """CREATE TABLE IF NOT EXISTS monthly_ration_lists (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL DEFAULT 'My Monthly Ration',
            is_active BOOLEAN DEFAULT TRUE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE,
            updated_at TIMESTAMP WITH TIME ZONE
        );""",
        """CREATE TABLE IF NOT EXISTS monthly_ration_items (
            id VARCHAR(36) PRIMARY KEY,
            list_id VARCHAR(36) NOT NULL REFERENCES monthly_ration_lists(id) ON DELETE CASCADE,
            product_id VARCHAR(50),
            product_name_en VARCHAR(150) NOT NULL,
            product_name_hi VARCHAR(150),
            unit VARCHAR(50) NOT NULL DEFAULT '1 kg',
            quantity INTEGER NOT NULL DEFAULT 1,
            notes VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE
        );""",'''

if 'monthly_ration_lists' not in content:
    content = content.replace(
        '"""CREATE TABLE IF NOT EXISTS notifications (',
        table_migrations + '\n        """CREATE TABLE IF NOT EXISTS notifications ('
    )

# 3. Add router include
if 'app.include_router(ration_lists.router' not in content:
    content = content.replace(
        'app.include_router(notifications.router, prefix=settings.API_V1_STR)',
        'app.include_router(notifications.router, prefix=settings.API_V1_STR)\napp.include_router(ration_lists.router, prefix=settings.API_V1_STR)'
    )

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated main.py with ration_lists router and migration statements')
