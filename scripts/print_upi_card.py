with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'checkout-opt-upi' in line:
        for j in range(max(0, i-2), min(len(lines), i+30)):
            print(f"{j+1}: {lines[j]}", end='')
        break
