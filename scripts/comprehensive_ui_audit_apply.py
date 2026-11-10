import os
from pathlib import Path

def patch_customer(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().replace("\r\n", "\n")

    # 1. Active Order Runner action buttons touch target (w-8 h-8 -> min-w-[44px] min-h-[44px] w-11 h-11)
    old_runner_actions = """                <div class="flex space-x-1.5">
                  <a id="runner-call-link" href="tel:9800000003" class="w-8 h-8 rounded-xl bg-white border border-slate-200 text-emerald-700 flex items-center justify-center shadow-xs active:scale-95 transition" title="Call Runner">
                    <i data-lucide="phone" class="w-3.5 h-3.5"></i>
                  </a>
                  <button onclick="openRunnerChatModal()" class="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-xs active:scale-95 transition" title="Message Runner">
                    <i data-lucide="message-square" class="w-3.5 h-3.5"></i>
                  </button>
                  <button onclick="shareCustomerConfirmedLocationPin()" class="w-8 h-8 rounded-xl bg-teal-600 text-white flex items-center justify-center shadow-xs active:scale-95 transition" title="Share Exact Doorstep Pin">
                    <i data-lucide="map-pin" class="w-3.5 h-3.5"></i>
                  </button>
                </div>"""

    new_runner_actions = """                <div class="flex items-center gap-2">
                  <a id="runner-call-link" href="tel:9800000003" class="min-w-[44px] min-h-[44px] w-11 h-11 rounded-xl bg-white border border-slate-200 text-emerald-700 flex items-center justify-center shadow-xs active:scale-95 transition" title="Call Runner">
                    <i data-lucide="phone" class="w-4 h-4"></i>
                  </a>
                  <button onclick="openRunnerChatModal()" class="min-w-[44px] min-h-[44px] w-11 h-11 rounded-xl bg-emerald-600 text-white flex items-center justify-center shadow-xs active:scale-95 transition" title="Message Runner">
                    <i data-lucide="message-square" class="w-4 h-4"></i>
                  </button>
                  <button onclick="shareCustomerConfirmedLocationPin()" class="min-w-[44px] min-h-[44px] w-11 h-11 rounded-xl bg-teal-600 text-white flex items-center justify-center shadow-xs active:scale-95 transition" title="Share Exact Doorstep Pin">
                    <i data-lucide="map-pin" class="w-4 h-4"></i>
                  </button>
                </div>"""

    if old_runner_actions in content:
        content = content.replace(old_runner_actions, new_runner_actions)

    # 2. Cancel order button height (min-h-[48px] h-12)
    old_cancel_btn = """                  <button onclick="cancelActiveOrderBinary()" id="cancel-order-btn" class="w-full py-2 px-3 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-300 font-bold rounded-xl flex items-center justify-center space-x-1.5 transition active:scale-95 text-xs">
                    <i data-lucide="x-circle" class="w-3.5 h-3.5"></i>
                    <span data-i18n="cancel_order_btn">Cancel Order (Full Refund)</span>
                  </button>"""

    new_cancel_btn = """                  <button onclick="cancelActiveOrderBinary()" id="cancel-order-btn" class="w-full min-h-[48px] h-12 py-3 px-4 bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-300 font-bold rounded-xl flex items-center justify-center space-x-2 transition active:scale-95 text-sm">
                    <i data-lucide="x-circle" class="w-4 h-4"></i>
                    <span data-i18n="cancel_order_btn">Cancel Order (Full Refund)</span>
                  </button>"""

    if old_cancel_btn in content:
        content = content.replace(old_cancel_btn, new_cancel_btn)

    # 3. Selected delivery address preview wrapping & change button touch target
    old_addr_card = """            <div id="checkout-selected-address-card" class="p-3 bg-emerald-50/60 rounded-xl border border-emerald-200 flex items-center justify-between text-xs">
              <div class="min-w-0 pr-2">
                <span class="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">Deliver to:</span>
                <p id="checkout-active-addr-title" class="font-bold text-slate-900 truncate">Home — Chaturshi, Muzaffarpur</p>
                <p id="checkout-active-addr-landmark" class="text-[11px] text-slate-600 truncate">Near Shiv Mandir</p>
              </div>
              <button type="button" onclick="openManageAddressesModal()" class="px-2.5 py-1.5 bg-white hover:bg-slate-50 text-emerald-800 border border-emerald-300 rounded-lg font-bold text-xs shrink-0 transition active:scale-95 shadow-2xs">
                Change
              </button>
            </div>"""

    new_addr_card = """            <div id="checkout-selected-address-card" class="p-3 bg-emerald-50/60 rounded-xl border border-emerald-200 flex flex-col sm:flex-row gap-2.5 sm:items-center sm:justify-between text-xs">
              <div class="min-w-0 pr-2">
                <span class="text-[10px] font-bold text-emerald-800 uppercase tracking-wider block">Deliver to:</span>
                <p id="checkout-active-addr-title" class="font-bold text-slate-900 break-words whitespace-normal leading-relaxed">Home — Chaturshi, Muzaffarpur</p>
                <p id="checkout-active-addr-landmark" class="text-[11px] text-slate-600 break-words whitespace-normal">Near Shiv Mandir</p>
              </div>
              <button type="button" onclick="openManageAddressesModal()" class="w-full sm:w-auto min-h-[44px] px-4 py-2 bg-white hover:bg-slate-50 text-emerald-800 border border-emerald-300 rounded-xl font-bold text-xs shrink-0 transition active:scale-95 shadow-2xs flex items-center justify-center">
                Change
              </button>
            </div>"""

    if old_addr_card in content:
        content = content.replace(old_addr_card, new_addr_card)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched customer app: {file_path}")


def patch_vendor(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().replace("\r\n", "\n")

    # Mark ready button min-h 48px
    old_mark_ready = """            <button onclick="markOrderReady('GB-8919')" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg text-xs shadow-sm transition active:scale-95 flex items-center justify-center space-x-1.5" data-i18n="mark_ready_btn">
              <i data-lucide="package-check" class="w-4 h-4"></i>
              <span>Mark Ready for Handover</span>
            </button>"""

    new_mark_ready = """            <button onclick="markOrderReady('GB-8919')" class="w-full min-h-[48px] h-12 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl text-sm shadow-sm transition active:scale-95 flex items-center justify-center space-x-2" data-i18n="mark_ready_btn">
              <i data-lucide="package-check" class="w-4 h-4"></i>
              <span>Mark Ready for Handover</span>
            </button>"""

    if old_mark_ready in content:
        content = content.replace(old_mark_ready, new_mark_ready)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched vendor app: {file_path}")


def patch_runner(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().replace("\r\n", "\n")

    # Confirm pickup button min-h 48px
    old_confirm_pickup = """            <button id="btn-confirm-pickup" onclick="confirmVendorPickup()" class="w-full py-3.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold shadow-md active:scale-95 transition flex items-center justify-center space-x-2" data-i18n="confirm_pickup_btn">
              <i data-lucide="package-check" class="w-4 h-4"></i>
              <span>Confirm Pickup (Start Delivery)</span>
            </button>"""

    new_confirm_pickup = """            <button id="btn-confirm-pickup" onclick="confirmVendorPickup()" class="w-full min-h-[48px] h-12 py-3 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-sm font-bold shadow-md active:scale-95 transition flex items-center justify-center space-x-2" data-i18n="confirm_pickup_btn">
              <i data-lucide="package-check" class="w-4 h-4"></i>
              <span>Confirm Pickup (Start Delivery)</span>
            </button>"""

    if old_confirm_pickup in content:
        content = content.replace(old_confirm_pickup, new_confirm_pickup)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched runner app: {file_path}")


if __name__ == "__main__":
    patch_customer("apps/admin/public/customer/index.html")
    patch_customer("public_web/customer/index.html")
    patch_vendor("apps/admin/public/vendor/index.html")
    patch_vendor("public_web/vendor/index.html")
    patch_runner("apps/admin/public/runner/index.html")
    patch_runner("public_web/runner/index.html")
