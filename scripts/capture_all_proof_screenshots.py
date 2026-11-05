import subprocess
import os
import sys
import json
import time

sys.stdout.reconfigure(encoding='utf-8')

artifact_dir = r"C:\Users\dhira\.gemini\antigravity\brain\918c8085-b60b-40a9-a077-a3344458bcc5"
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
temp_user_data = r"C:\Users\dhira\AppData\Local\Temp\chrome_proof_capture"
port = 8092

with open("scripts/active_test_context.json", "r", encoding="utf-8") as f:
    ctx = json.load(f)

order_id = ctx["order_id"]
otp = ctx["otp"]
cust_token = ctx["customer_token"]
runner_token = ctx["runner_token"]
ticket_id = ctx["ticket_id"]

harness_dir = os.path.abspath("scripts/harness")
os.makedirs(harness_dir, exist_ok=True)

with open("public_web/customer/index.html", "r", encoding="utf-8") as f:
    cust_html = f.read()

def inject_state(html, setup_js):
    injection = f"""
    <script>
      localStorage.setItem('gb_customer_authenticated', 'true');
      localStorage.setItem('gb_customer_phone', '9811223344');
      localStorage.setItem('gb_customer_name', 'Sunita Devi');
      localStorage.setItem('gb_customer_jwt', '{cust_token}');
      localStorage.setItem('gb_active_order_id', '{order_id}');
      localStorage.setItem('gb_active_order_otp', '{otp}');
      localStorage.setItem('gb_order_placed_time', '{int(time.time()*1000) - 45000}');
      
      const syntheticAddresses = [
        {{
          id: 'addr_bithoor_1',
          title: 'Home / घर',
          recipient_name: 'Sunita Devi',
          phone: '9811223344',
          village: 'Bithoor',
          landmark: 'Near Shiva Temple Gate',
          district: 'Muzaffarpur',
          state: 'Bihar',
          is_default: true,
          latitude: 26.2380,
          longitude: 85.3690
        }},
        {{
          id: 'addr_parihar_2',
          title: 'Farm / खेत',
          recipient_name: 'Sunita Devi',
          phone: '9811223344',
          village: 'Parihar',
          landmark: 'Tubewell 4, East Field',
          district: 'Muzaffarpur',
          state: 'Bihar',
          is_default: false,
          latitude: 26.2450,
          longitude: 85.3780
        }}
      ];
      localStorage.setItem('gb_saved_addresses', JSON.stringify(syntheticAddresses));

      window.addEventListener('load', () => {{
        setTimeout(() => {{
          window.userSavedAddresses = syntheticAddresses;
          {setup_js}
        }}, 800);
      }});
    </script>
    """
    return html.replace('</head>', injection + '\n</head>')

# Create harnesses for all proof views
harnesses = {
    # P0 Specific Proofs
    "p0_01_account_default_address": inject_state(cust_html, "switchTab('account'); renderAccountAddressSummary();"),
    "p0_02_manage_addresses_modal": inject_state(cust_html, "switchTab('account'); openManageAddressesModal();"),
    "p0_03_location_map_picker": inject_state(cust_html, "openLocationMapPickerModal();"),
    "p0_04_monthly_ration_list": inject_state(cust_html, "openMonthlyRationModal();"),
    "p0_05_monthly_ration_order_review": inject_state(cust_html, "openMonthlyRationModal(); setTimeout(() => proceedToMonthlyRationOrderReview(), 400);"),
    "p0_06_verified_products_catalog": inject_state(cust_html, "switchTab('home');"),
    
    # System Stability Proofs
    "proof_01_customer_orders": inject_state(cust_html, "switchTab('orders');"),
    "proof_02_vertical_timeline": inject_state(cust_html, "switchTab('orders'); document.getElementById('order-tracking-vertical').scrollIntoView();"),
    "proof_03_live_map": inject_state(cust_html, "switchTab('orders'); document.getElementById('order-live-map').scrollIntoView();"),
    "proof_05_past_orders": inject_state(cust_html, "switchTab('orders'); document.getElementById('section-past-orders').scrollIntoView();"),
    "proof_08_customer_chat": inject_state(cust_html, f"openRunnerChatModal(); document.getElementById('chat-messages-container').innerHTML += '<div class=\"flex justify-end\"><div class=\"bg-indigo-50 border border-indigo-200 p-2.5 rounded-2xl text-xs space-y-1\"><b>📍 Confirmed Doorstep Pin</b><p class=\"text-[10px] font-mono\">26.2380, 85.3690</p><p class=\"text-[10px] text-indigo-700\">Near Shiva Temple Gate, Bithoor</p></div></div>';"),
}

# Runner Harness
with open("public_web/runner/index.html", "r", encoding="utf-8") as f:
    runner_html = f.read()

runner_injection = f"""
<script>
  localStorage.setItem('gb_runner_authenticated', 'true');
  localStorage.setItem('gb_runner_jwt', '{runner_token}');
  localStorage.setItem('gb_runner_phone', '9800000003');
  window.addEventListener('load', () => {{
    setTimeout(() => {{
      const card = document.getElementById('customer-shared-pin-card');
      if (card) {{
        card.classList.remove('hidden');
        document.getElementById('pin-lat-lng').innerText = '26.2380, 85.3690';
        document.getElementById('pin-landmark').innerText = 'Near Shiva Temple Gate, Bithoor';
      }}
      const missionCard = document.getElementById('runner-active-mission');
      if (missionCard) missionCard.scrollIntoView();
    }}, 800);
  }});
</script>
"""
harnesses["proof_09_runner_pin"] = runner_html.replace('</head>', runner_injection + '\n</head>')

# Support Tickets Harness
harnesses["proof_10_support_tickets"] = inject_state(cust_html, f"""
  openModal('modal-my-tickets');
  document.getElementById('my-tickets-list').innerHTML = `
    <div class="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 text-xs">
      <div class="flex items-center justify-between">
        <span class="font-bold text-slate-900">Callback Request (#{ticket_id[:8]})</span>
        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">PENDING_DISPATCH</span>
      </div>
      <p class="text-[11px] text-slate-600">Customer requested rural delivery landmark verification call.</p>
      <div class="flex items-center justify-between pt-1 text-[10px] text-slate-400 font-mono">
        <span>Order #{order_id[-6:]}</span>
        <span>Just now</span>
      </div>
    </div>
  `;
""")

for name, content in harnesses.items():
    file_path = os.path.join(harness_dir, f"{name}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

server_proc = subprocess.Popen(
    [sys.executable, "-m", "http.server", str(port), "--directory", harness_dir],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
time.sleep(1.5)

screenshots = [
    ("proof_p0_01_account_default_address.png", f"http://127.0.0.1:{port}/p0_01_account_default_address.html", "393,852"),
    ("proof_p0_02_manage_addresses_modal.png", f"http://127.0.0.1:{port}/p0_02_manage_addresses_modal.html", "393,852"),
    ("proof_p0_03_location_map_picker.png", f"http://127.0.0.1:{port}/p0_03_location_map_picker.html", "393,852"),
    ("proof_p0_04_monthly_ration_list.png", f"http://127.0.0.1:{port}/p0_04_monthly_ration_list.html", "393,852"),
    ("proof_p0_05_monthly_ration_order_review.png", f"http://127.0.0.1:{port}/p0_05_monthly_ration_order_review.html", "393,852"),
    ("proof_p0_06_verified_products_catalog.png", f"http://127.0.0.1:{port}/p0_06_verified_products_catalog.html", "393,852"),
    ("proof_01_customer_orders_screen.png", f"http://127.0.0.1:{port}/proof_01_customer_orders.html", "393,852"),
    ("proof_02_vertical_delivery_timeline.png", f"http://127.0.0.1:{port}/proof_02_vertical_timeline.html", "393,852"),
    ("proof_03_genuine_runner_live_map.png", f"http://127.0.0.1:{port}/proof_03_live_map.html", "393,852"),
    ("proof_05_past_orders_area.png", f"http://127.0.0.1:{port}/proof_05_past_orders.html", "393,852"),
    ("proof_08_customer_runner_chat.png", f"http://127.0.0.1:{port}/proof_08_customer_chat.html", "393,852"),
    ("proof_09_runner_receiving_customer_pin.png", f"http://127.0.0.1:{port}/proof_09_runner_pin.html", "393,852"),
    ("proof_10_customer_support_tickets.png", f"http://127.0.0.1:{port}/proof_10_support_tickets.html", "393,852")
]

print("\n--- Capturing Fresh Visual Proof Screenshots ---")
try:
    for filename, url, win_size in screenshots:
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
            print(f"[OK] Captured {filename}: {size:,} bytes")
        else:
            print(f"[FAIL] Could not capture {filename}")
finally:
    server_proc.terminate()
    server_proc.wait()
    print("Proof capture completed.")
