import shutil
import hashlib

def get_hash(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

sync_targets = [
    # Customer
    ('public_web/customer/index.html', 'apps/customer/web/index.html'),
    ('public_web/customer/index.html', 'customer_pwa.html'),
    ('public_web/customer/index.html', 'C:/Users/dhira/OneDrive/Desktop/gh-pages/customer/index.html'),
    # Vendor
    ('public_web/vendor/index.html', 'apps/vendor/web/index.html'),
    ('public_web/vendor/index.html', 'vendor_pwa.html'),
    ('public_web/vendor/index.html', 'C:/Users/dhira/OneDrive/Desktop/gh-pages/vendor/index.html'),
    # Runner
    ('public_web/runner/index.html', 'apps/runner/web/index.html'),
    ('public_web/runner/index.html', 'runner_pwa.html'),
    ('public_web/runner/index.html', 'C:/Users/dhira/OneDrive/Desktop/gh-pages/runner/index.html'),
]

for src, dst in sync_targets:
    shutil.copy2(src, dst)
    src_h = get_hash(src)
    dst_h = get_hash(dst)
    assert src_h == dst_h, f"Hash mismatch between {src} and {dst}"
    print(f"Synced {src} -> {dst} (SHA256: {src_h[:8]}...)")

print("All targets successfully synced and verified.")
