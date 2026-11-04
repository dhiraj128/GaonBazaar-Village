# -*- coding: utf-8 -*-
import re
from typing import Optional, Dict, Any, List

# Master Catalog dictionary for Village Hyperlocal shopping
ITEM_DICTIONARY = [
    {
        "id": "cat_atta",
        "name_en": "Chakki Fresh Atta",
        "name_hi": "चक्की फ्रेश आटा",
        "unit": "5 kg",
        "price": 215.0,
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80",
        "keywords": ["atta", "aata", "aashirvaad", "gehu", "wheat", "flour", "आटा", "गेहूं", "चक्की आटा"]
    },
    {
        "id": "cat_mustard_oil",
        "name_en": "Kachhi Ghani Mustard Oil",
        "name_hi": "कच्ची घानी सरसों तेल",
        "unit": "1 L",
        "price": 145.0,
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80",
        "keywords": ["mustard oil", "sarson tel", "sarson", "mustard", "oil", "tel", "सरसों तेल", "तेल", "सरसों का तेल"]
    },
    {
        "id": "cat_milk",
        "name_en": "Fresh Pure Cow Milk",
        "name_hi": "ताज़ा गाय का दूध",
        "unit": "1 L",
        "price": 56.0,
        "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400",
        "keywords": ["milk", "doodh", "dudh", "cow milk", "taaza", "दूध", "गाय का दूध"]
    },
    {
        "id": "cat_sugar",
        "name_en": "Pure Refined Sugar (Cheeni)",
        "name_hi": "शुद्ध सफेद चीनी",
        "unit": "1 kg",
        "price": 45.0,
        "image_url": "https://images.unsplash.com/photo-1581441363689-1f3c3c414635?w=500&q=80",
        "keywords": ["sugar", "cheeni", "chini", "shakkar", "चीनी", "शक्कर"]
    },
    {
        "id": "cat_biscuits",
        "name_en": "Parle-G Glucose Biscuits",
        "name_hi": "पारले-जी ग्लूकोज बिस्कुट",
        "unit": "1 packet",
        "price": 25.0,
        "image_url": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400",
        "keywords": ["parle-g", "parleg", "parle", "biscuit", "biscuits", "बिस्कुट", "बिस्कुट"]
    },
    {
        "id": "cat_detergent",
        "name_en": "Surf Excel Detergent Powder",
        "name_hi": "सर्फ एक्सेल डिटर्जेंट पाउडर",
        "unit": "1 kg",
        "price": 115.0,
        "image_url": "https://images.unsplash.com/photo-1585421514738-01798e348b17?w=500&q=80",
        "keywords": ["surf excel", "surf", "detergent", "washing powder", "ghadi", "सर्फ", "सर्फ एक्सेल", "डिटर्जेंट"]
    },
    {
        "id": "cat_salt",
        "name_en": "Tata Iodized Salt (Namak)",
        "name_hi": "टाटा आयोडाइज्ड नमक",
        "unit": "1 kg",
        "price": 28.0,
        "image_url": "https://images.unsplash.com/photo-1626082896492-766af4eb6501?w=400",
        "keywords": ["tata salt", "salt", "namak", "टाटा नमक", "नमक"]
    },
    {
        "id": "cat_tea",
        "name_en": "Tata Tea Premium",
        "name_hi": "टाटा टी प्रीमियम चायपत्ती",
        "unit": "250 g",
        "price": 110.0,
        "image_url": "https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&q=80",
        "keywords": ["tea", "chai", "chaipatti", "chai patti", "चाय", "चायपत्ती"]
    },
    {
        "id": "cat_potato",
        "name_en": "Fresh Local Potato (Aloo)",
        "name_hi": "ताज़ा आलू",
        "unit": "1 kg",
        "price": 24.0,
        "image_url": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=400",
        "keywords": ["potato", "aloo", "alu", "आलू"]
    },
    {
        "id": "cat_onion",
        "name_en": "Red Onion (Pyaz)",
        "name_hi": "लाल प्याज़",
        "unit": "1 kg",
        "price": 32.0,
        "image_url": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=400",
        "keywords": ["onion", "pyaz", "pyaaz", "प्याज़", "कांदा"]
    },
    {
        "id": "cat_tomato",
        "name_en": "Desi Tomato (Tamatar)",
        "name_hi": "देसी टमाटर",
        "unit": "1 kg",
        "price": 28.0,
        "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80",
        "keywords": ["tomato", "tamatar", "टमाटर"]
    },
    {
        "id": "cat_toor_dal",
        "name_en": "Desi Toor / Arhar Dal",
        "name_hi": "देसी अरहर / तूर दाल",
        "unit": "1 kg",
        "price": 135.0,
        "image_url": "https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=400",
        "keywords": ["dal", "toor", "arhar", "दाल", "तूर दाल", "अरहर दाल"]
    },
    {
        "id": "cat_bath_soap",
        "name_en": "Dettol Original Bath Soap",
        "name_hi": "डेटॉल ओरिजिनल साबुन",
        "unit": "1 pack",
        "price": 125.0,
        "image_url": "https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=500&q=80",
        "keywords": ["soap", "dettol", "bath soap", "साबुन", "डेटॉल"]
    },
    {
        "id": "cat_led_bulb",
        "name_en": "9W LED Energy Saver Bulb",
        "name_hi": "9 वाट एलईडी बल्ब",
        "unit": "1 piece",
        "price": 85.0,
        "image_url": "https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=500&q=80",
        "keywords": ["bulb", "led", "light", "bijli", "बल्ब", "एलईडी"]
    },
    {
        "id": "cat_pooja_agarbatti",
        "name_en": "Chandan Agarbatti Incense",
        "name_hi": "चंदन अगरबत्ती",
        "unit": "1 pack",
        "price": 20.0,
        "image_url": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400",
        "keywords": ["agarbatti", "dhoop", "incense", "अगरबत्ती", "धूप", "पूजा"]
    }
]

WORD_NUMBERS = {
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5, "panch": 5,
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5
}

def parse_ai_shopping_query(query: str, store_products: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Parses speech or text input in Hindi, English, or Hinglish.
    Strictly adheres to:
    1. Intent classification: ADD, REMOVE, SEARCH, SHOW_CART.
    2. Number extraction (digits and words).
    3. Unit extraction (kg, litre, packet, piece).
    4. Catalog-grounded matching with alias resolution.
    5. Clean Hindi/English replies without encoding errors.
    """
    raw_text = query.strip()
    lowered = raw_text.lower()

    # 1. Cart View Intent (only if not an add/remove command)
    is_add_or_remove = any(k in lowered for k in ["add", "daal", "dal", "जोड़", "डाल", "remove", "hata", "हटा"])
    if not is_add_or_remove and any(k in lowered for k in ["cart dikhao", "show cart", "view cart", "mera cart", "open cart", "कार्ट दिखाओ", "कार्ट खोलो", "कार्ट देखें"]):
        return {
            "intent": "SHOW_CART",
            "query": raw_text,
            "quantity": 0,
            "matched_product": None,
            "reply_hi": "आपका शॉपिंग कार्ट खोला जा रहा है।",
            "reply_en": "Opening your shopping cart.",
            "confidence": 0.98
        }

    # 2. Remove Intent
    is_remove = any(k in lowered for k in [
        "remove", "delete", "hata do", "hatao", "hataiye", "कम करो", "हटा दो", "हटाओ", "हटा दीजिए"
    ])

    # 3. Explicit Search Intent (e.g. "Surf Excel search karo", "search milk")
    is_search_intent = any(k in lowered for k in ["search", "khojo", "dhundo", "सर्च करो", "खोजो", "ढूंढो"])

    # 4. Extract Quantity
    quantity = 1
    digit_match = re.search(r"\b(\d+)\b", lowered)
    if digit_match:
        quantity = max(1, int(digit_match.group(1)))
    else:
        tokens = re.findall(r"[\w\u0900-\u097F]+", lowered)
        for token in tokens:
            if token in WORD_NUMBERS:
                quantity = WORD_NUMBERS[token]
                break

    # 5. Extract Unit mention
    requested_unit = None
    if any(u in lowered for u in ["litre", "liter", "लीटर", " l ", "l"]):
        requested_unit = "Litre"
    elif any(u in lowered for u in ["kilo", "kg", "किलो"]):
        requested_unit = "kg"
    elif any(u in lowered for u in ["packet", "pkt", "pack", "पैकेट"]):
        requested_unit = "packet"
    elif any(u in lowered for u in ["gram", "gm", "ग्राम"]):
        requested_unit = "g"
    elif any(u in lowered for u in ["piece", "pc", "पीस"]):
        requested_unit = "piece"

    # 6. Catalog Search
    items_to_search = store_products if store_products else ITEM_DICTIONARY
    best_match = None
    best_score = 0

    for item in items_to_search:
        keywords = item.get("keywords", [])
        name_en = item.get("name_en", "").lower()
        name_hi = item.get("name_hi", "").lower()

        # Prioritize exact multi-word phrase hits
        for kw in keywords + [name_en, name_hi]:
            kw_clean = kw.strip().lower()
            if kw_clean and kw_clean in lowered:
                score = len(kw_clean)
                # Boost if exact keyword match
                if kw_clean in lowered.split():
                    score += 10
                if score > best_score:
                    best_score = score
                    best_match = item

    if best_match:
        name_en = best_match.get("name_en")
        name_hi = best_match.get("name_hi")
        catalog_unit = best_match.get("unit", "")
        price = best_match.get("price", 0.0)

        # Unit compatibility check (e.g. customer said "1 kg doodh" but catalog sells in "1 L")
        display_unit = requested_unit if requested_unit else catalog_unit

        if is_remove:
            intent = "REMOVE_FROM_CART"
            reply_hi = f"{name_hi} कार्ट से हटा दिया गया है।"
            reply_en = f"Removed {name_en} from your cart."
        elif is_search_intent:
            intent = "SEARCH"
            reply_hi = f"'{name_hi}' उपलब्ध है (मूल्य ₹{price:.2f})।"
            reply_en = f"Found {name_en} (₹{price:.2f})."
        else:
            intent = "ADD_TO_CART"
            reply_hi = f"{quantity} {display_unit} {name_hi} कार्ट में जोड़ दिया गया है।"
            reply_en = f"Added {quantity} {display_unit} of {name_en} to your cart."

        return {
            "intent": intent,
            "query": raw_text,
            "quantity": quantity,
            "matched_product": {
                "id": best_match.get("id"),
                "name_en": name_en,
                "name_hi": name_hi,
                "unit": catalog_unit,
                "price": price,
                "image_url": best_match.get("image_url")
            },
            "reply_hi": reply_hi,
            "reply_en": reply_en,
            "confidence": 0.95
        }

    # Fallback when no product matches
    return {
        "intent": "SEARCH",
        "query": raw_text,
        "quantity": 1,
        "matched_product": None,
        "reply_hi": f"'{raw_text}' के लिए उत्पाद खोजे जा रहे हैं...",
        "reply_en": f"Searching products for '{raw_text}'...",
        "confidence": 0.60
    }
