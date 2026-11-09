import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

def inspect_app(app_name):
    path = f'public_web/{app_name}/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n==================== {app_name.upper()} ====================")
    for i in range(1, 8):
        m = re.search(rf'(<div[^>]*id=[\"\']screen-onboarding-{i}[\"\'].*?)(?=<div[^>]*id=[\"\']screen-onboarding-|\n\s*<script|$)', content, re.DOTALL)
        if m:
            snippet = m.group(1)[:400].replace('\n', ' ')
            # get all headings / titles inside this screen
            headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', m.group(1), re.DOTALL)
            clean_headings = [re.sub(r'<[^>]+>', '', h).strip() for h in headings]
            inputs = re.findall(r'<input[^>]*id=[\"\']([^\"\']+)[\"\']', m.group(1))
            selects = re.findall(r'<select[^>]*id=[\"\']([^\"\']+)[\"\']', m.group(1))
            buttons = re.findall(r'<button[^>]*onclick=[\"\']([^\"\']+)[\"\']', m.group(1))
            print(f"--- SCREEN ONBOARDING-{i} ---")
            print(f"Headings: {clean_headings}")
            print(f"Inputs: {inputs}")
            print(f"Selects: {selects}")
            print(f"Buttons (onclick): {buttons[:3]}")

inspect_app('runner')
inspect_app('vendor')
