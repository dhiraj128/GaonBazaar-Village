import subprocess
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_user_data = r"C:\Users\dhira\AppData\Local\Temp\chrome_console_audit"
port = 8089
pages_dir = r"C:\Users\dhira\OneDrive\Desktop\gh-pages"

server_proc = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(port), "--directory", pages_dir],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

try:
    for app in ["customer", "vendor", "runner", "admin"]:
        url = f"http://127.0.0.1:{port}/{app}/"
        cmd = [
            chrome_path,
            "--headless=new",
            "--disable-gpu",
            "--dump-dom",
            f"--user-data-dir={temp_user_data}",
            url
        ]
        res = subprocess.run(cmd, capture_output=True, timeout=15)
        dom = res.stdout.decode('utf-8', errors='ignore')
        print(f"[{app.upper()}] DOM size: {len(dom):,} characters. Contains body: {'<body' in dom.lower()}")
finally:
    server_proc.terminate()
    server_proc.wait()
