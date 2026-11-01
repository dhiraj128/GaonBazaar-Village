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
