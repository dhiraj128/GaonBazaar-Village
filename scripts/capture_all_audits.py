import subprocess
import os

artifact_dir = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_user_data = r"C:\Users\dhira\AppData\Local\Temp\chrome_audit_tmp"

targets = [
    ("customer_prelaunch_audit.png", "https://dhiraj128.github.io/GaonBazar-Village/customer/", "412,915"),
    ("vendor_prelaunch_audit.png", "https://dhiraj128.github.io/GaonBazar-Village/vendor/", "412,915"),
    ("runner_prelaunch_audit.png", "https://dhiraj128.github.io/GaonBazar-Village/runner/", "412,915"),
    ("admin_prelaunch_audit.png", "https://dhiraj128.github.io/GaonBazar-Village/admin/", "1280,800"),
]

for filename, url, win_size in targets:
    out_path = os.path.join(artifact_dir, filename)
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        f"--user-data-dir={temp_user_data}",
        f"--window-size={win_size}",
        f"--screenshot={out_path}",
        url
    ]
    res = subprocess.run(cmd, capture_output=True, timeout=30)
    if os.path.exists(out_path):
        size = os.path.getsize(out_path)
        print(f"Captured {filename}: {size} bytes")
    else:
        print(f"Failed to capture {filename}")

print("Visual regression capture complete.")
