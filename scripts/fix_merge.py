with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

old_str = """      if (msgs.length === 0 && (!window.customerOrderMessages || window.customerOrderMessages.length === 0)) {
        msgs = [
          {
            id: "msg_init_runner",
            sender_role: "runner",
            sender_name: "Delivery Partner",
            message_type: "TEXT",
            content: "Namaste! I have picked up your groceries from Sharma Kirana. I am riding towards your village now.",
            created_at: new Date(Date.now() - 300000).toISOString()
          }
        ];
      } else if (window.customerOrderMessages && window.customerOrderMessages.length > 0) {
        // Merge any locally created messages
        msgs = [...msgs, ...window.customerOrderMessages.filter(lm => !msgs.some(m => m.id === lm.id))];
      }"""

new_str = """      if (msgs.length === 0) {
        msgs = [
          {
            id: "msg_init_runner",
            sender_role: "runner",
            sender_name: "Delivery Partner",
            message_type: "TEXT",
            content: "Namaste! I have picked up your groceries from Sharma Kirana. I am riding towards your village now.",
            created_at: new Date(Date.now() - 300000).toISOString()
          }
        ];
      }
      if (window.customerOrderMessages && window.customerOrderMessages.length > 0) {
        // Merge any locally created messages
        msgs = [...msgs, ...window.customerOrderMessages.filter(lm => !msgs.some(m => m.id === lm.id))];
      }"""

assert old_str in c, "Could not find old_str"
c = c.replace(old_str, new_str, 1)

with open('public_web/customer/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Merge logic fixed successfully!")
