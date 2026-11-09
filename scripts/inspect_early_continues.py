import sys

sys.stdout.reconfigure(encoding='utf-8')

for name in ['customer', 'runner', 'vendor']:
    with open(f'public_web/{name}/index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"\n==================== {name.upper()} ====================")
    # Search for all occurrences of "continue" or "आगे बढ़ें" in the first 600 lines
    lines = html.splitlines()[:600]
    for idx, l in enumerate(lines, start=1):
        if any(w in l.lower() for w in ['continue', 'proceed', 'आगे']):
            print(f"{idx}: {l.strip()}")
