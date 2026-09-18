from src.slots import extract_slots, get_missing_slots

def test_get_missing_slots():
    state = {"rainfall": 500}
    missing = get_missing_slots(state)
    assert "land_use" in missing
    assert "rainfall" not in missing
