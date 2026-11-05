import urllib.request

candidates = [
    'https://dhiraj128.github.io/GaonBazar-Village/',
    'https://dhiraj128.github.io/GaonBazar-Village/index.html',
    'https://dhiraj128.github.io/gaonbazar-village/',
    'https://dhiraj128.github.io/gaonbazar-village/customer/',
    'https://dhiraj128.github.io/GaonBazar-Village/customer/index.html',
    'https://dhiraj128.github.io/GaoBazar-Village/',
    'https://dhiraj128.github.io/GaoBazar-Village/customer/',
    'https://dhiraj128.github.io/GaoBazar-Village/customer/index.html'
]

for url in candidates:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            print(f"[FOUND {resp.status}] {url}")
    except urllib.error.HTTPError as e:
        print(f"[{e.code}] {url}")
    except Exception as e:
        print(f"[ERR] {url}: {e}")
