with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Declare openModal and closeModal in global scope
global_modal_funcs = """    // Explicit global modal helper proxies
    function openModal(modalId) {
      if (typeof window.openModal === 'function') {
        window.openModal(modalId);
      } else {
        const m = document.getElementById(modalId);
        if (m) {
          m.classList.remove('hidden');
          m.classList.add('flex');
        }
      }
    }
    window.openModalProxy = openModal;

    function closeModal(modalId) {
      if (typeof window.closeModal === 'function') {
        window.closeModal(modalId);
      } else {
        const m = document.getElementById(modalId);
        if (m) {
          m.classList.add('hidden');
          m.classList.remove('flex');
        }
      }
    }
    window.closeModalProxy = closeModal;
"""

# Place it right before openPaymentSettingsModal
target = "function openPaymentSettingsModal() {"
if target in text:
    text = text.replace(target, global_modal_funcs + "\n    " + target, 1)
    with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Added global modal proxies to customer/index.html")
else:
    print("Target not found")
