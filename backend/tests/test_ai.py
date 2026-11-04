# -*- coding: utf-8 -*-
import pytest
from app.services.ai_service import parse_ai_shopping_query

def test_ai_query_hindi_atta():
    result = parse_ai_shopping_query("दो किलो आटा कार्ट में जोड़ें")
    assert result["intent"] == "ADD_TO_CART"
    assert result["quantity"] == 2
    assert "atta" in result["matched_product"]["id"]
    assert "आटा" in result["reply_hi"]

def test_ai_query_hinglish_milk():
    result = parse_ai_shopping_query("doodh ek litre chahiye")
    assert result["intent"] == "ADD_TO_CART"
    assert result["quantity"] == 1
    assert "milk" in result["matched_product"]["id"]

def test_ai_query_show_cart():
    result = parse_ai_shopping_query("मेरा कार्ट दिखाओ")
    assert result["intent"] == "SHOW_CART"

def test_ai_query_remove():
    result = parse_ai_shopping_query("दूध हटा दो")
    assert result["intent"] == "REMOVE_FROM_CART"
    assert "milk" in result["matched_product"]["id"]

def test_ai_query_mandatory_phrases():
    # 1. '1 kg doodh add karo'
    res = parse_ai_shopping_query("1 kg doodh add karo")
    assert res["intent"] == "ADD_TO_CART"
    assert res["quantity"] == 1
    assert "milk" in res["matched_product"]["id"]

    # 2. '1 litre doodh add karo'
    res = parse_ai_shopping_query("1 litre doodh add karo")
    assert res["intent"] == "ADD_TO_CART"
    assert res["quantity"] == 1
    assert "milk" in res["matched_product"]["id"]

    # 3. 'एक लीटर दूध डाल दो'
    res = parse_ai_shopping_query("एक लीटर दूध डाल दो")
    assert res["intent"] == "ADD_TO_CART"
    assert res["quantity"] == 1
    assert "milk" in res["matched_product"]["id"]

    # 4. '2 kilo atta add karo'
    res = parse_ai_shopping_query("2 kilo atta add karo")
    assert res["intent"] == "ADD_TO_CART"
    assert res["quantity"] == 2
    assert "atta" in res["matched_product"]["id"]

    # 5. '1 kg sugar chahiye'
    res = parse_ai_shopping_query("1 kg sugar chahiye")
    assert res["intent"] == "ADD_TO_CART"
    assert res["quantity"] == 1
    assert "sugar" in res["matched_product"]["id"]

    # 6. 'Sarson tel 1 litre add karo'
    res = parse_ai_shopping_query("Sarson tel 1 litre add karo")
    assert res["intent"] == "ADD_TO_CART"
    assert res["quantity"] == 1
    assert "mustard_oil" in res["matched_product"]["id"]

    # 7. 'Surf Excel search karo'
    res = parse_ai_shopping_query("Surf Excel search karo")
    assert res["intent"] in ["SEARCH", "ADD_TO_CART"]
    assert "detergent" in res["matched_product"]["id"]

    # 8. 'Biscuit add karo'
    res = parse_ai_shopping_query("Biscuit add karo")
    assert res["intent"] == "ADD_TO_CART"
    assert res["quantity"] == 1
    assert "biscuits" in res["matched_product"]["id"]

    # 9. 'Doodh remove karo'
    res = parse_ai_shopping_query("Doodh remove karo")
    assert res["intent"] == "REMOVE_FROM_CART"
    assert "milk" in res["matched_product"]["id"]

    # 10. 'Cart dikhao'
    res = parse_ai_shopping_query("Cart dikhao")
    assert res["intent"] == "SHOW_CART"

    # 11. 'Do packet Parle-G add karo'
    res = parse_ai_shopping_query("Do packet Parle-G add karo")
    assert res["intent"] == "ADD_TO_CART"
    assert res["quantity"] == 2
    assert "biscuits" in res["matched_product"]["id"]
