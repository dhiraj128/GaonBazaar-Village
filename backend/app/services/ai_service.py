import re
from typing import Optional, Dict, Any, List

# Catalog aliases for village items
ITEM_DICTIONARY = [
    {
        "id": "cat_atta",
        "name_en": "Chakki Fresh Atta",
        "name_hi": "ताज़ा चक्की आटा",
        "unit": "1 kg",
        "price": 38.0,
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&q=80",
        "keywords": ["atta", "aata", "gehu", "wheat", "आटा", "flour"]
    },
    {
        "id": "cat_rice",
        "name_en": "Basmati Rice (Minapur Special)",
        "name_hi": "बासमती चावल",
        "unit": "1 kg",
        "price": 54.0,
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=400",
        "keywords": ["rice", "chawal", "चावल", "basmati", "paddy"]
    },
    {
        "id": "cat_mustard_oil",
        "name_en": "Kachhi Ghani Mustard Oil",
        "name_hi": "कच्ची घानी सरसों तेल",
        "unit": "1 L",
        "price": 142.0,
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=500&q=80",
        "keywords": ["oil", "tel", "sarson", "mustard", "सरसों तेल", "तेल"]
    },
    {
        "id": "cat_milk",
        "name_en": "Fresh Cow Milk",
        "name_hi": "ताज़ा गाय का दूध",
        "unit": "1 L",
        "price": 56.0,
        "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400",
        "keywords": ["milk", "doodh", "dudh", "दूध", "cow milk"]
    },
    {
        "id": "cat_potato",
        "name_en": "Fresh Local Potato (Aloo)",
        "name_hi": "ताज़ा देशी आलू",
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
        "keywords": ["onion", "pyaz", "pyaaz", "कांदा", "प्याज"]
    },
    {
        "id": "cat_tomato",
        "name_en": "Desi Tomato (Tamatar)",
        "name_hi": "देशी लाल टमाटर",
        "unit": "1 kg",
        "price": 28.0,
        "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80",
        "keywords": ["tomato", "tamatar", "टमाटर"]
    },
    {
        "id": "cat_pooja_agarbatti",
        "name_en": "Chandan Agarbatti Incense",
        "name_hi": "चंदन अगरबत्ती",
        "unit": "1 pack",
        "price": 20.0,
        "image_url": "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400",
        "keywords": ["agarbatti", "dhoop", "incense", "अगरबत्ती", "pooja", "पूजा"]
    },
    {
        "id": "cat_led_bulb",
        "name_en": "9W LED Energy Saver Bulb",
        "name_hi": "९ वॉट एलईडी बल्ब",
        "unit": "1 piece",
        "price": 85.0,
        "image_url": "https://images.unsplash.com/photo-1550985543-f47f38aeee65?w=500&q=80",
        "keywords": ["bulb", "led", "बल्ब", "light", "bijli", "बिजली"]
    }
]

HINDI_NUMBERS = {
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5, "panch": 5,
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पाँच": 5, "पांच": 5,
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5
}

def parse_ai_shopping_query(query: str, store_products: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Parses speech or text input in Hindi, English, or Hinglish.
    Identifies intent, quantity, and matched catalog item.
    """
    raw_text = query.strip()
    lowered = raw_text.lower()
    
    # Check for Cart View intent
    if any(k in lowered for k in ["cart dikhao", "show cart", "view cart", "mera cart", "कार्ट दिखाओ", "टोकरी दिखाओ"]):
        return {
            "intent": "SHOW_CART",
            "query": raw_text,
            "quantity": 0,
            "matched_product": None,
            "reply_hi": "आपका कार्ट खोला जा रहा है।",
            "reply_en": "Opening your shopping cart.",
            "confidence": 0.98
        }
    
    # Check for Remove intent
    is_remove = any(k in lowered for k in ["hata do", "remove", "delete", "hatao", "हटा दो", "हटाओ"])
    
    # Extract quantity (digits or word numbers)
    quantity = 1
    digit_match = re.search(r"\b(\d+)\b", lowered)
    if digit_match:
        quantity = max(1, int(digit_match.group(1)))
    else:
        tokens = lowered.split()
        for token in tokens:
            if token in HINDI_NUMBERS:
                quantity = HINDI_NUMBERS[token]
                break
                
    # Search in available store products or global dictionary
    items_to_search = store_products if store_products else ITEM_DICTIONARY
    best_match = None
    best_score = 0
    
    for item in items_to_search:
        keywords = item.get("keywords", [])
        name_en = item.get("name_en", "").lower()
        name_hi = item.get("name_hi", "").lower()
        
        # Check direct keyword or substring hits
        for kw in keywords + [name_en, name_hi]:
            if kw and kw in lowered:
                score = len(kw)
                if score > best_score:
                    best_score = score
                    best_match = item
                    
    if best_match:
        intent = "REMOVE_FROM_CART" if is_remove else "ADD_TO_CART"
        name_en = best_match.get("name_en")
        name_hi = best_match.get("name_hi")
        unit = best_match.get("unit")
        price = best_match.get("price")
        
        if is_remove:
            reply_hi = f"{name_hi} कार्ट से हटा दिया गया।"
            reply_en = f"Removed {name_en} from your cart."
        else:
            reply_hi = f"{quantity} {unit} {name_hi} कार्ट में जोड़ दिया गया है।"
            reply_en = f"Added {quantity} {unit} of {name_en} to your cart."
            
        return {
            "intent": intent,
            "query": raw_text,
            "quantity": quantity,
            "matched_product": {
                "id": best_match.get("id"),
                "name_en": name_en,
                "name_hi": name_hi,
                "unit": unit,
                "price": price,
                "image_url": best_match.get("image_url")
            },
            "reply_hi": reply_hi,
            "reply_en": reply_en,
            "confidence": 0.95
        }
    
    # Generic search intent if product name not strictly recognized
    return {
        "intent": "SEARCH",
        "query": raw_text,
        "quantity": 1,
        "matched_product": None,
        "reply_hi": f"'{raw_text}' के लिए सामान खोजा जा रहा है...",
        "reply_en": f"Searching items for '{raw_text}'...",
        "confidence": 0.65
    }
