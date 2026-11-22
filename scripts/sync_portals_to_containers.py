"""
GaonBazaar Portal & Container Synchronization Script
Ensures all static portals across apps/admin/public, apps/*/web, android_containers/*/www,
and android_containers/*/android/app/src/main/assets/public are completely synchronized
with compiled local Tailwind CSS, native visibility safeguards, and hardened scripts.
"""

import os
import shutil
import hashlib

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADMIN_PUBLIC = os.path.join(REPO_ROOT, "apps", "admin", "public")

def sha256_file(filepath):
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def sync_portal(app_name):
    src_dir = os.path.join(ADMIN_PUBLIC, app_name)
    css_file = f"{app_name}.css"
    
    # Destination directories
    targets = [
        os.path.join(REPO_ROOT, "apps", app_name, "web"),
        os.path.join(REPO_ROOT, "public_web", app_name),
        os.path.join(REPO_ROOT, "android_containers", app_name, "www"),
        os.path.join(REPO_ROOT, "android_containers", app_name, "android", "app", "src", "main", "assets", "public"),
    ]
    
    print(f"\n--- Syncing {app_name.upper()} Portal ---")
    
    # Read canonical source files
    src_index = os.path.join(src_dir, "index.html")
    with open(src_index, "r", encoding="utf-8") as f:
        index_content = f.read()

    # In android containers, ensure relative paths for script src
    container_index_content = index_content.replace(f'src="/{app_name}/', 'src="./')
    
    for target_dir in targets:
        if not os.path.exists(target_dir):
            print(f"Skipping non-existent: {target_dir}")
            continue
            
        # Copy CSS
        src_css_path = os.path.join(src_dir, css_file)
        if os.path.exists(src_css_path):
            shutil.copy2(src_css_path, os.path.join(target_dir, css_file))
            
        # Copy all JS scripts
        for fname in os.listdir(src_dir):
            if fname.endswith(".js") or fname.endswith(".json") or fname.endswith(".png"):
                shutil.copy2(os.path.join(src_dir, fname), os.path.join(target_dir, fname))
                
        # Write container index.html with relative script paths
        dest_index = os.path.join(target_dir, "index.html")
        with open(dest_index, "w", encoding="utf-8") as f:
            f.write(container_index_content)
            
        print(f"Synced {app_name} -> {os.path.relpath(target_dir, REPO_ROOT)}")

if __name__ == "__main__":
    for app in ["customer", "vendor", "runner"]:
        sync_portal(app)
    print("\n[SUCCESS] All portals and Android containers successfully synchronized.")
