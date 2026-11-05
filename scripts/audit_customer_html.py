import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/customer/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all event handlers in HTML
handlers = re.findall(r'on[a-z]+\s*=\s*["\']([^"\']+)["\']', content, re.IGNORECASE)
called_funcs = set()
for h in handlers:
    matches = re.findall(r'([a-zA-Z0-9_$]+)\s*\(', h)
    for m in matches:
        called_funcs.add(m)

# Find all function calls in addEventListener('DOMContentLoaded'...) or throughout script
script_matches = re.findall(r'<script.*?>([\s\S]*?)</script>', content)
script_text = '\n'.join(script_matches)

# Extract defined functions
defined_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_$]+)\s*\(', script_text))
defined_funcs.update(re.findall(r'(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\(', script_text))
defined_funcs.update(re.findall(r'(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*function', script_text))

# Check functions called in DOMContentLoaded or init
init_match = re.search(r"addEventListener\('DOMContentLoaded',[\s\S]*?\}\);", script_text)
if init_match:
    init_calls = re.findall(r'([a-zA-Z0-9_$]+)\s*\(', init_match.group(0))
    for c in init_calls:
        called_funcs.add(c)

builtins = {
    'event', 'alert', 'confirm', 'prompt', 'parseInt', 'parseFloat',
    'setTimeout', 'setInterval', 'clearInterval', 'clearTimeout',
    'if', 'for', 'while', 'catch'
}

print('=== AUDIT OF CALLED FUNCTIONS ===')
missing = []
for fn in sorted(called_funcs):
    if fn not in defined_funcs and fn not in builtins:
        missing.append(fn)
        print(f'MISSING / UNDEFINED: {fn}')

print(f'\nTotal missing functions: {len(missing)}')
