with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = """    function toastWarning(msg) {
      Toastify({
        text: msg,
        duration: 2800,
        gravity: "top",
        position: "center",
        style: {
          background: "#d97706",
          borderRadius: "14px",
          fontSize: "12px",
          fontWeight: "600"
        }
      }).showToast();
    }"""

replacement = target + """

    function toastInfo(msg) {
      if (typeof Toastify === 'function') {
        Toastify({
          text: msg,
          duration: 2500,
          gravity: "top",
          position: "center",
          style: {
            background: "#0284c7",
            borderRadius: "14px",
            fontSize: "12px",
            fontWeight: "600",
            boxShadow: "0 4px 12px rgba(2, 132, 199, 0.3)"
          }
        }).showToast();
      } else {
        console.log("INFO:", msg);
      }
    }
    window.toastInfo = toastInfo;"""

if target in content:
    content = content.replace(target, replacement, 1)
    with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: toastInfo added to customer/index.html")
else:
    print("Target not found!")
