import urllib.request

candidates = {
    'atta_pkg': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80',
    'oil_bottle': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80',
    'salt_pack': 'https://images.unsplash.com/photo-1626197031507-c17099753214?w=500&q=80',
    'detergent': 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=500&q=80',
    'sugar': 'https://images.unsplash.com/photo-1587132137056-bfbf0166836e?w=500&q=80',
    'rice': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400',
    'milk': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400',
    'dal': 'https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=500&q=80',
    'biscuits': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400',
    'tomato': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80',
    'potato': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400',
    'onion': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400'
}

for name, url in candidates.items():
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"{name}: {resp.status} length={resp.headers.get('Content-Length')}")
    except Exception as e:
        print(f"{name}: FAIL ({e})")
