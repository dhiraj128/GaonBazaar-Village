import re

for app in ['customer', 'vendor', 'runner']:
    path = f'public_web/{app}/index.html'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()

        events = re.findall(r'on[a-z]+\s*=\s*["\']([^"\']+)["\']', text, re.IGNORECASE)
        called_funcs = set()
        for ev in events:
            matches = re.findall(r'([a-zA-Z0-9_$]+)\s*\(', ev)
            for m in matches:
                if m not in ['if', 'alert', 'console', 'confirm', 'event', 'setTimeout', 'stopPropagation', 'preventDefault', 'Number', 'parseInt', 'parseFloat']:
                    called_funcs.add(m)

        declared_funcs = set(re.findall(r'function\s+([a-zA-Z0-9_$]+)\s*\(', text))
        declared_funcs.update(re.findall(r'(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\(?', text))
        declared_funcs.update(re.findall(r'window\.([a-zA-Z0-9_$]+)\s*=', text))

        missing = [f for f in called_funcs if f not in declared_funcs]
        print(f'=== {app.upper()} ===')
        print('Total called:', len(called_funcs))
        print('Missing called functions:', sorted(missing))
    except Exception as e:
        print(f'{app}: {e}')
