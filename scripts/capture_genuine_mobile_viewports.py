import subprocess
import os
import sys
import time
import socket

sys.stdout.reconfigure(encoding='utf-8')

artifact_dir = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_user_data = r"C:\Users\dhira\AppData\Local\Temp\chrome_genuine_viewports"
pages_dir = r"C:\Users\dhira\OneDrive\Desktop\gh-pages"
port = 8089

# Start local server
print(f"Starting local HTTP server for gh-pages assets on port {port}...")
server_proc = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(port), "--directory", pages_dir],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

# Wait for server to bind
time.sleep(1.5)

targets = [
    # Customer Viewports
    ("customer_viewport_360.png", f"http://127.0.0.1:{port}/customer/", "360,800"),
    ("customer_viewport_393.png", f"http://127.0.0.1:{port}/customer/", "393,851"),
    ("customer_viewport_412.png", f"http://127.0.0.1:{port}/customer/", "412,915"),
    # Vendor Viewports
    ("vendor_viewport_360.png", f"http://127.0.0.1:{port}/vendor/", "360,800"),
    ("vendor_viewport_393.png", f"http://127.0.0.1:{port}/vendor/", "393,851"),
    ("vendor_viewport_412.png", f"http://127.0.0.1:{port}/vendor/", "412,915"),
    # Runner Viewports
    ("runner_viewport_360.png", f"http://127.0.0.1:{port}/runner/", "360,800"),
    ("runner_viewport_393.png", f"http://127.0.0.1:{port}/runner/", "393,851"),
    ("runner_viewport_412.png", f"http://127.0.0.1:{port}/runner/", "412,915"),
    # Admin Viewports
    ("admin_viewport_mobile_393.png", f"http://127.0.0.1:{port}/admin/", "393,851"),
    ("admin_viewport_desktop_1280.png", f"http://127.0.0.1:{port}/admin/", "1280,800"),
]

print("Capturing genuine mobile viewports across Customer, Vendor, Runner, and Admin...")
try:
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
        res = subprocess.run(cmd, capture_output=True, timeout=25)
        if os.path.exists(out_path):
            size = os.path.getsize(out_path)
            print(f"[OK] Captured {filename} ({win_size}): {size:,} bytes")
        else:
            print(f"[FAIL] Could not capture {filename}")
finally:
    print("Terminating local server...")
    server_proc.terminate()
    server_proc.wait()
    print("Done.")
