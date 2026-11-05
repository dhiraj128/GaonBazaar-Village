import subprocess
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

artifact_dir = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_user_data = r"C:\Users\dhira\AppData\Local\Temp\chrome_audit_viewports"

targets = [
    # Customer
    ("customer_viewport_360.png", "https://dhiraj128.github.io/GaonBazar-Village/customer/", "360,800"),
    ("customer_viewport_393.png", "https://dhiraj128.github.io/GaonBazar-Village/customer/", "393,851"),
    ("customer_viewport_412.png", "https://dhiraj128.github.io/GaonBazar-Village/customer/", "412,915"),
    # Vendor
    ("vendor_viewport_360.png", "https://dhiraj128.github.io/GaonBazar-Village/vendor/", "360,800"),
    ("vendor_viewport_393.png", "https://dhiraj128.github.io/GaonBazar-Village/vendor/", "393,851"),
    ("vendor_viewport_412.png", "https://dhiraj128.github.io/GaonBazar-Village/vendor/", "412,915"),
    # Runner
    ("runner_viewport_360.png", "https://dhiraj128.github.io/GaonBazar-Village/runner/", "360,800"),
    ("runner_viewport_393.png", "https://dhiraj128.github.io/GaonBazar-Village/runner/", "393,851"),
    ("runner_viewport_412.png", "https://dhiraj128.github.io/GaonBazar-Village/runner/", "412,915"),
    # Admin
    ("admin_viewport_mobile_393.png", "https://dhiraj128.github.io/GaonBazar-Village/admin/", "393,851"),
    ("admin_viewport_desktop_1280.png", "https://dhiraj128.github.io/GaonBazar-Village/admin/", "1280,800"),
]

print("Starting mobile viewport multi-resolution browser audit...")
for filename, url, win_size in targets:
    out_path = os.path.join(artifact_dir, filename)
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--user-data-dir={temp_user_data}",
        f"--window-size={win_size}",
        f"--screenshot={out_path}",
        url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=30)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 0:
            print(f"[OK] Captured {filename} ({win_size}): {os.path.getsize(out_path)} bytes")
        else:
            print(f"[FAIL] Could not capture {filename}")
    except Exception as e:
        print(f"[ERR] Error capturing {filename}: {e}")

print("Mobile viewport multi-resolution browser audit completed successfully.")
