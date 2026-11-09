import sys

sys.stdout.reconfigure(encoding='utf-8')

for app in ['runner', 'vendor']:
    path = f'public_web/{app}/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace('",,', '",')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed double comma in runner and vendor")
