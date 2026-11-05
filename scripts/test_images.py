import urllib.request

candidates = {
    # Sugar
    'sugar_bowl': 'https://images.unsplash.com/photo-1587132137056-bfbf0166836e?w=500&q=80',
    'sugar_cubes': 'https://images.unsplash.com/photo-1622484212850-eb596d769edc?w=500&q=80',
    # Salt
    'salt_shaker': 'https://images.unsplash.com/photo-1626197031507-c17099753214?w=500&q=80',
    'salt_pile': 'https://images.unsplash.com/photo-1608686207856-001b95cf60ca?w=500&q=80',
    'salt_bowl': 'https://images.unsplash.com/photo-1518110903415-32e5b77c1d76?w=500&q=80',
    # Detergent
    'detergent_clean': 'https://images.unsplash.com/photo-1585336261026-7788463573e0?w=500&q=80',
    'detergent_powder': 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?w=500&q=80',
    'detergent_box': 'https://images.unsplash.com/photo-1610557892470-55d9e80c0bce?w=500&q=80',
    # Flour/Atta
    'flour_sack': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80',
    'flour_bowl': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=500&q=80',
    # Oil
    'mustard_oil': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80',
}

for name, url in candidates.items():
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f'{name}: {resp.status} length={resp.headers.get("Content-Length")}')
    except Exception as e:
        print(f'{name}: FAIL ({e})')
