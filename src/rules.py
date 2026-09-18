from typing import List, Dict, Any, Tuple

def evaluate_card_preconditions(card: Dict[str, Any], state: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Evaluates a single card against the user's state.
    Returns (True, "") if it passes.
    Returns (False, "reason") if it fails.
    """
    preconditions = card.get('preconditions', {})
    
    # 1. min_rainfall / max_rainfall
    rainfall = state.get('rainfall')
    if rainfall is not None:
        if 'min_rainfall' in preconditions and rainfall < preconditions['min_rainfall']:
            return False, f"Rainfall ({rainfall}mm) is below minimum required ({preconditions['min_rainfall']}mm)"
        if 'max_rainfall' in preconditions and rainfall > preconditions['max_rainfall']:
            return False, f"Rainfall ({rainfall}mm) exceeds maximum allowed ({preconditions['max_rainfall']}mm)"
            
    # 2. min_ph / max_ph
    ph = state.get('ph')
    if ph is not None:
        if 'min_ph' in preconditions and ph < preconditions['min_ph']:
            return False, f"Soil pH ({ph}) is too acidic (min {preconditions['min_ph']})"
        if 'max_ph' in preconditions and ph > preconditions['max_ph']:
            return False, f"Soil pH ({ph}) is too alkaline (max {preconditions['max_ph']})"
            
    # 3. land_use (array of permitted uses)
    user_land_use = state.get('land_use')
    if user_land_use and 'land_use' in preconditions:
        permitted = preconditions['land_use']
        if user_land_use not in permitted:
            return False, f"Land use '{user_land_use}' is not suitable for this intervention (requires one of {permitted})"
            
    # 4. slope_percent
    slope = state.get('slope_percent')
    if slope is not None:
        if 'min_slope_percent' in preconditions and slope < preconditions['min_slope_percent']:
            return False, f"Slope ({slope}%) is too flat (min {preconditions['min_slope_percent']}%)"
        if 'max_slope_percent' in preconditions and slope > preconditions['max_slope_percent']:
            return False, f"Slope ({slope}%) is too steep (max {preconditions['max_slope_percent']}%)"
            
    # 5. has_water_body (boolean)
    has_water = state.get('has_water_body')
    if has_water is not None:
        if 'has_water_body' in preconditions and preconditions['has_water_body'] and not has_water:
            return False, "Requires an adjacent water body"
            
    return True, ""

def filter_cards(cards: List[Dict[str, Any]], state: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Applies hard preconditions to all cards.
    Returns:
      passed_cards: list of card dicts that survive
      rejections: list of dicts {"card_id": "...", "reason": "..."}
    """
    passed = []
    rejections = []
    
    for card in cards:
        is_valid, reason = evaluate_card_preconditions(card, state)
        if is_valid:
            passed.append(card)
        else:
            rejections.append({
                "card_id": card["id"],
                "reason": reason
            })
            
    return passed, rejections
