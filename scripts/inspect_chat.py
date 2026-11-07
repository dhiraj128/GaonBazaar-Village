import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    cust = f.read()

pos = cust.find('id="chat-input-text"')
print(cust[pos-300:pos+800])
