import os
from pathlib import Path

def patch_runner_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("\r\n", "\n")

    # 1. 6-digit OTP boxes: flex justify-center items-center gap-1.5 sm:gap-2 max-w-full
    content = content.replace(
        '<div class="flex justify-between space-x-1.5 max-w-[320px] mx-auto">',
        '<div class="flex justify-center items-center gap-1.5 sm:gap-2 max-w-full mx-auto px-1">'
    )

    # 2. Aadhaar OTP input min-height 48px
    content = content.replace(
        'class="w-full text-center py-3 rounded-xl border border-slate-300 bg-white text-slate-900 font-mono font-extrabold text-lg tracking-widest focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs"',
        'class="w-full min-h-[48px] h-12 text-center py-3 rounded-xl border-2 border-slate-300 bg-white text-slate-900 font-mono font-extrabold text-xl tracking-widest focus:border-blue-600 focus:ring-2 focus:ring-blue-100 focus:outline-none shadow-xs"'
    )

    # 3. Fleet help buttons in Runner app: flex-col sm:flex-row with full width & min 48px height
    old_fleet_desk = """          <div class="grid grid-cols-2 gap-3">
            <a href="tel:18002007766" onclick="toastInfo('Calling Fleet Desk 1800-200-7766...')" class="py-3 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-2 shadow-xs active:scale-95 transition">
              <i data-lucide="phone" class="w-4 h-4"></i>
              <span data-i18n="call_fleet_desk">Call Fleet Desk</span>
            </a>
            <a href="https://wa.me/919711002233" target="_blank" onclick="toastInfo('Opening WhatsApp Fleet Support...')" class="py-3 px-3 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs font-bold flex items-center justify-center space-x-2 shadow-xs active:scale-95 transition">
              <i data-lucide="message-square" class="w-4 h-4"></i>
              <span data-i18n="whatsapp_chat">WhatsApp Chat</span>
            </a>
          </div>"""

    new_fleet_desk = """          <div class="flex flex-col sm:flex-row gap-3 w-full">
            <a href="tel:18002007766" onclick="toastInfo('Calling Fleet Desk 1800-200-7766...')" class="w-full sm:flex-1 min-h-[48px] h-12 py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center space-x-2 shadow-xs active:scale-95 transition">
              <i data-lucide="phone" class="w-4 h-4"></i>
              <span data-i18n="call_fleet_desk" class="whitespace-normal">Call Fleet Desk</span>
            </a>
            <a href="https://wa.me/919711002233" target="_blank" onclick="toastInfo('Opening WhatsApp Fleet Support...')" class="w-full sm:flex-1 min-h-[48px] h-12 py-3 px-4 bg-emerald-700 hover:bg-emerald-800 text-white rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center space-x-2 shadow-xs active:scale-95 transition">
              <i data-lucide="message-square" class="w-4 h-4"></i>
              <span data-i18n="whatsapp_chat" class="whitespace-normal">WhatsApp Chat</span>
            </a>
          </div>"""

    if old_fleet_desk in content:
        content = content.replace(old_fleet_desk, new_fleet_desk)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched additional runner fixes in {file_path}")


def patch_vendor_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("\r\n", "\n")

    # 1. 6-digit OTP boxes: flex justify-center items-center gap-1.5 sm:gap-2 max-w-full
    content = content.replace(
        '<div class="flex justify-between space-x-1.5 max-w-[320px] mx-auto">',
        '<div class="flex justify-center items-center gap-1.5 sm:gap-2 max-w-full mx-auto px-1">'
    )

    # 2. Aadhaar OTP input
    content = content.replace(
        'class="w-full text-center py-3.5 rounded-xl border border-slate-300 bg-white text-slate-900 font-mono font-extrabold text-lg tracking-widest focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs"',
        'class="w-full min-h-[48px] h-12 text-center py-3.5 rounded-xl border-2 border-slate-300 bg-white text-slate-900 font-mono font-extrabold text-xl tracking-widest focus:border-emerald-600 focus:ring-2 focus:ring-emerald-100 focus:outline-none shadow-xs"'
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched additional vendor fixes in {file_path}")


def patch_customer_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace("\r\n", "\n")

    # 1. 6-digit OTP boxes: flex justify-center items-center gap-1.5 sm:gap-2 max-w-full
    content = content.replace(
        '<div class="flex justify-between space-x-1.5 max-w-[320px] mx-auto">',
        '<div class="flex justify-center items-center gap-1.5 sm:gap-2 max-w-full mx-auto px-1">'
    )

    # 2. Aadhaar OTP input min-height 48px
    content = content.replace(
        'class="w-full text-center py-3 bg-white border border-slate-300 focus:border-emerald-600 focus:outline-none rounded-xl text-lg font-mono font-bold tracking-widest text-slate-900 shadow-2xs"',
        'class="w-full min-h-[48px] h-12 text-center py-3 bg-white border-2 border-slate-300 focus:border-emerald-600 focus:outline-none rounded-xl text-xl font-mono font-bold tracking-widest text-slate-900 shadow-2xs"'
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched customer fixes in {file_path}")


def patch_react_components():
    # KycUsersView.tsx
    kyc_path = Path("apps/admin/src/components/KycUsersView.tsx")
    with open(kyc_path, "r", encoding="utf-8") as f:
        kyc_content = f.read().replace("\r\n", "\n")

    old_kyc_footer = """            {/* Modal Action Buttons: Approve & Activate vs Reject */}
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between sticky bottom-0">
              <button
                onClick={() => setShowRejectModal(true)}
                disabled={isActionSubmitting}
                className="px-4 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs rounded-xl border border-rose-300 transition flex items-center space-x-1.5"
              >
                <XCircle className="w-4 h-4" />
                <span>{t.rejectApplication}</span>
              </button>

              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setSelectedDetail(null)}
                  className="px-4 py-2.5 text-slate-600 hover:text-slate-900 text-xs font-semibold"
                >
                  {t.cancel}
                </button>
                <button
                  onClick={handleApproveAction}
                  disabled={isActionSubmitting}
                  className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs rounded-xl shadow-md transition flex items-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>{t.approveAndActivate}</span>
                </button>
              </div>
            </div>"""

    new_kyc_footer = """            {/* Modal Action Buttons: Approve & Activate vs Reject */}
            <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between sticky bottom-0">
              <button
                onClick={() => setShowRejectModal(true)}
                disabled={isActionSubmitting}
                className="w-full sm:w-auto min-h-[44px] px-4 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-700 font-bold text-xs rounded-xl border border-rose-300 transition flex items-center justify-center space-x-1.5"
              >
                <XCircle className="w-4 h-4" />
                <span>{t.rejectApplication}</span>
              </button>

              <div className="flex flex-col sm:flex-row items-center gap-2 w-full sm:w-auto">
                <button
                  onClick={() => setSelectedDetail(null)}
                  className="w-full sm:w-auto min-h-[44px] px-4 py-2.5 text-slate-600 hover:text-slate-900 text-xs font-semibold flex items-center justify-center"
                >
                  {t.cancel}
                </button>
                <button
                  onClick={handleApproveAction}
                  disabled={isActionSubmitting}
                  className="w-full sm:w-auto min-h-[44px] px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs rounded-xl shadow-md transition flex items-center justify-center space-x-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>{t.approveAndActivate}</span>
                </button>
              </div>
            </div>"""

    if old_kyc_footer in kyc_content:
        kyc_content = kyc_content.replace(old_kyc_footer, new_kyc_footer)
        with open(kyc_path, "w", encoding="utf-8") as f:
            f.write(kyc_content)
        print("Patched KycUsersView.tsx successfully!")

    # OrdersGodModeView.tsx
    orders_path = Path("apps/admin/src/components/OrdersGodModeView.tsx")
    with open(orders_path, "r", encoding="utf-8") as f:
        orders_content = f.read().replace("\r\n", "\n")

    old_force_cancel = """              {/* Power 3: Force Cancel Order */}
              <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex items-center justify-between">
                <div>
                  <h5 className="text-xs font-extrabold text-rose-950">
                    {t.forceCancel}
                  </h5>
                  <p className="text-[11px] text-rose-700">
                    {lang === 'hi'
                      ? 'स्थिति को CANCELLED में बदलता है और स्वचालित रूप से पूर्ण रिफंड जारी करता है।'
                      : 'Changes status to CANCELLED and triggers instant automated refund logic.'}
                  </p>
                </div>
                <button
                  onClick={handleExecuteCancel}
                  disabled={isGodActionLoading}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-xl shadow-xs transition"
                >
                  {t.forceCancel}
                </button>
              </div>"""

    new_force_cancel = """              {/* Power 3: Force Cancel Order */}
              <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
                <div>
                  <h5 className="text-xs font-extrabold text-rose-950">
                    {t.forceCancel}
                  </h5>
                  <p className="text-[11px] text-rose-700">
                    {lang === 'hi'
                      ? 'स्थिति को CANCELLED में बदलता है और स्वचालित रूप से पूर्ण रिफंड जारी करता है।'
                      : 'Changes status to CANCELLED and triggers instant automated refund logic.'}
                  </p>
                </div>
                <button
                  onClick={handleExecuteCancel}
                  disabled={isGodActionLoading}
                  className="w-full sm:w-auto min-h-[44px] px-5 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-bold text-xs rounded-xl shadow-xs transition flex items-center justify-center shrink-0"
                >
                  {t.forceCancel}
                </button>
              </div>"""

    if old_force_cancel in orders_content:
        orders_content = orders_content.replace(old_force_cancel, new_force_cancel)
        with open(orders_path, "w", encoding="utf-8") as f:
            f.write(orders_content)
        print("Patched OrdersGodModeView.tsx successfully!")


if __name__ == "__main__":
    patch_runner_html("apps/admin/public/runner/index.html")
    patch_runner_html("public_web/runner/index.html")
    patch_vendor_html("apps/admin/public/vendor/index.html")
    patch_vendor_html("public_web/vendor/index.html")
    patch_customer_html("apps/admin/public/customer/index.html")
    patch_customer_html("public_web/customer/index.html")
    patch_react_components()
