from typing import List, Dict, Any

def resolve_conflicts(cards: List[Dict[str, Any]], scores: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Greedy conflict resolution based on scores.
    Sorts cards by score descending. If a card conflicts with an already selected card, it is dropped.
    """
    # Sort cards by their score, highest first
    sorted_cards = sorted(cards, key=lambda c: scores.get(c['id'], 0.0), reverse=True)
    
    selected_cards = []
    selected_ids = set()
    
    for card in sorted_cards:
        conflicts = set(card.get('conflicts_with', []))
        
        # Check if this card conflicts with anything we've already selected
        if not conflicts.isdisjoint(selected_ids):
            continue
            
        selected_cards.append(card)
        selected_ids.add(card['id'])
        
    return selected_cards

def score_cards(cards: List[Dict[str, Any]], state: Dict[str, Any]) -> Dict[str, float]:
    """
    Multi-metric scoring function.
    A card scores higher if it:
      - Moves several metrics across different domains (water, soil, biodiversity)
      - Has high evidence confidence
      - Directly addresses the user's stated problem (if known)
    Incorporates coupled-effect logic explicitly.
    """
    user_goal = state.get("goal") # e.g. "reduce erosion" or "improve water"
    
    scores = {}
    for card in cards:
        base_score = 0.0
        effects = card.get('effects', [])
        
        domains_hit = set()
        
        for effect in effects:
            metric_id = effect['metric_id']
            confidence = effect['confidence_score']
            value_change = effect['value_change']
            
            # 1. Base value based on magnitude and confidence
            # Normalize changes loosely (e.g. 10% SOC vs 40mm water) - we just use a generic multiplier
            # We assume positive value_change is good for SOC, WHC, Biodiversity. 
            # Negative is good for erosion. Let's absolute it for impact magnitude.
            impact = abs(value_change) * confidence
            
            # Domain mapping
            if "soc" in metric_id or "erosion" in metric_id:
                domains_hit.add("soil")
            elif "water" in metric_id:
                domains_hit.add("water")
            elif "biodiversity" in metric_id or "pollinator" in metric_id:
                domains_hit.add("habitat")
                
            base_score += impact
            
            # User goal alignment boost
            if user_goal:
                if user_goal.lower() in metric_id:
                    base_score += 50.0 # heavy boost for addressing stated problem
                    
        # 2. Domain diversity multiplier
        # The more domains an intervention improves, the better (resilience)
        domain_multiplier = 1.0 + (0.5 * (len(domains_hit) - 1)) if domains_hit else 1.0
        
        # 3. Coupled-effect logic
        # If a card increases SOC (Soil Organic Carbon), we explicitly boost the score 
        # to credit downstream water-holding capacity and microbial diversity benefits,
        # treating the system as coupled rather than independent metrics.
        has_soc = any("soc" in e['metric_id'] and e['value_change'] > 0 for e in effects)
        coupled_boost = 20.0 if has_soc else 0.0
        
        final_score = (base_score * domain_multiplier) + coupled_boost
        scores[card['id']] = final_score
        
    return scores
