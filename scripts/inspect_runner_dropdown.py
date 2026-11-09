with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    r_content = f.read()

idx = r_content.find('function handleRunnerVillageSearch')
print("=== RUNNER VILLAGE SEARCH ===")
print(r_content[idx:idx+1500].encode('ascii', errors='replace').decode('ascii'))
