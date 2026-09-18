import pytest
from src.rules import evaluate_card_preconditions, filter_cards

def test_evaluate_card_preconditions():
    card = {
        "id": "test_card",
        "preconditions": {
            "min_rainfall": 400,
            "max_ph": 8.0,
            "land_use": ["arable", "pasture"]
        }
    }
    
    # 1. Passes all
    state = {"rainfall": 500, "ph": 7.5, "land_use": "arable"}
    valid, reason = evaluate_card_preconditions(card, state)
    assert valid is True
    assert reason == ""
    
    # 2. Fails rainfall
    state = {"rainfall": 300, "ph": 7.5, "land_use": "arable"}
    valid, reason = evaluate_card_preconditions(card, state)
    assert valid is False
    assert "Rainfall" in reason
    
    # 3. Fails pH
    state = {"rainfall": 500, "ph": 8.5, "land_use": "arable"}
    valid, reason = evaluate_card_preconditions(card, state)
    assert valid is False
    assert "Soil pH" in reason
    
    # 4. Fails land use
    state = {"rainfall": 500, "ph": 7.5, "land_use": "forest"}
    valid, reason = evaluate_card_preconditions(card, state)
    assert valid is False
    assert "Land use" in reason

def test_filter_cards():
    cards = [
        {"id": "card_1", "preconditions": {"min_rainfall": 500}},
        {"id": "card_2", "preconditions": {"min_rainfall": 200}},
    ]
    
    state = {"rainfall": 300}
    
    passed, rejections = filter_cards(cards, state)
    
    assert len(passed) == 1
    assert passed[0]["id"] == "card_2"
    
    assert len(rejections) == 1
    assert rejections[0]["card_id"] == "card_1"
