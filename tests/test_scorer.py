import pytest
from src.scorer import score_cards, resolve_conflicts

def test_score_cards():
    cards = [
        {
            "id": "card_multi_domain",
            "effects": [
                {"metric_id": "soc_percent", "value_change": 10.0, "confidence_score": 0.9},
                {"metric_id": "water_holding_capacity", "value_change": 15.0, "confidence_score": 0.8}
            ]
        },
        {
            "id": "card_single_domain",
            "effects": [
                {"metric_id": "soil_erosion_rate", "value_change": -30.0, "confidence_score": 0.9}
            ]
        }
    ]
    
    state = {}
    scores = score_cards(cards, state)
    
    # card_multi_domain hits 2 domains (soil, water) and gets a domain multiplier (1.5)
    # AND it gets the coupled-effect SOC boost (20.0)
    # card_single_domain hits 1 domain (soil) and gets no boost
    
    assert scores["card_multi_domain"] > scores["card_single_domain"]
    
    # Test user goal boost
    state_goal = {"goal": "erosion"}
    scores_goal = score_cards(cards, state_goal)
    assert scores_goal["card_single_domain"] > scores["card_single_domain"]

def test_resolve_conflicts():
    cards = [
        {"id": "card_A", "conflicts_with": ["card_B"]},
        {"id": "card_B", "conflicts_with": ["card_A"]},
        {"id": "card_C", "conflicts_with": []}
    ]
    
    # B scores higher than A, so A should be dropped
    scores = {
        "card_A": 50.0,
        "card_B": 80.0,
        "card_C": 60.0
    }
    
    resolved = resolve_conflicts(cards, scores)
    
    assert len(resolved) == 2
    ids = [c["id"] for c in resolved]
    assert "card_B" in ids
    assert "card_C" in ids
    assert "card_A" not in ids
