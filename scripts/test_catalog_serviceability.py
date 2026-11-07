import json, sys, os, re

print("--- Testing Master Catalog & Serviceability Implementation ---")

# 1. Test Vendor App HTML & Logic
with open('public_web/vendor/index.html', 'r', encoding='utf-8') as f:
    vendor_html = f.read()

assert 'id="modal-add-product"' in vendor_html, "modal-add-product exists"
print("[PASS] modal-add-product exists")

assert 'id="catalog-library-search"' in vendor_html, "catalog-library-search input exists"
print("[PASS] catalog-library-search input exists")

assert 'id="master-catalog-results"' in vendor_html, "master-catalog-results exists"
print("[PASS] master-catalog-results container exists")

assert re.search(r'id=["\']new-item-name["\'][^>]*readonly', vendor_html), "new-item-name is read-only"
print("[PASS] new-item-name is read-only")

assert re.search(r'id=["\']new-item-brand["\'][^>]*readonly', vendor_html), "new-item-brand is read-only"
print("[PASS] new-item-brand is read-only")

assert re.search(r'id=["\']new-item-mrp["\'][^>]*readonly', vendor_html), "new-item-mrp is read-only"
print("[PASS] new-item-mrp is read-only")

assert 'id="new-item-price"' in vendor_html and 'id="new-item-price" readonly' not in vendor_html, "new-item-price is editable"
print("[PASS] new-item-price is editable by vendor")

assert 'id="new-item-stock"' in vendor_html and 'id="new-item-stock" readonly' not in vendor_html, "new-item-stock is editable"
print("[PASS] new-item-stock is editable by vendor")

assert 'id="btn-add-to-live-store"' in vendor_html, "btn-add-to-live-store button exists"
print("[PASS] btn-add-to-live-store button exists")

assert "const MASTER_SKU_DATABASE =" in vendor_html, "MASTER_SKU_DATABASE defined"
print("[PASS] MASTER_SKU_DATABASE defined in Vendor JS")


# 2. Test Customer App HTML & Logic
with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    cust_html = f.read()

assert 'id="service-unreachable-banner"' in cust_html, "service-unreachable-banner exists on Home tab"
print("[PASS] service-unreachable-banner exists on Home tab")

assert 'id="cart-service-unreachable-banner"' in cust_html, "cart-service-unreachable-banner exists on Cart tab"
print("[PASS] cart-service-unreachable-banner exists on Cart tab")

assert "within an 8.0 km radius" not in cust_html, "Static 8.0 km text removed from about"
assert "within an 8km radius" not in cust_html, "Static 8km text removed from FAQ"
print("[PASS] Static 8km radius claims removed from user-facing copy")

assert "function checkServiceability" in cust_html, "checkServiceability function exists"
print("[PASS] checkServiceability function defined in Customer JS")

print("\n--- ALL STATIC & DOM CHECKS PASSED ---")
