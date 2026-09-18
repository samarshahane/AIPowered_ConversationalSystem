import json
from typing import Dict, Any, List, Optional
from src.llm import call_llm_json

# Required slots for a confident recommendation
REQUIRED_SLOTS = ["rainfall", "land_use"]

# Allowed categorical values
VALID_LAND_USES = ["arable", "pasture", "orchard", "forest", "degraded", "wetland"]

def extract_slots(text: str) -> Dict[str, Any]:
    """
    Uses the LLM to extract numeric and categorical variables from free text.
    Validates and normalizes units.
    """
    schema_prompt = """
    Extract environmental variables from the text into this JSON schema:
    {
      "rainfall": int (in mm),
      "ph": float (0.0 to 14.0),
      "slope_percent": float,
      "has_water_body": bool,
      "land_use": string (one of: arable, pasture, orchard, forest, degraded, wetland),
      "goal": string
    }
    Only output valid JSON.
    """
    
    full_prompt = f"{schema_prompt}\n\nUser Text:\n{text}"
    
    try:
        extracted = call_llm_json(full_prompt, "environmental_slots")
    except Exception as e:
        print(f"LLM extraction failed: {e}")
        return {}
        
    # Validation / Normalisation
    validated = {}
    
    if "rainfall" in extracted and isinstance(extracted["rainfall"], (int, float)):
        validated["rainfall"] = float(extracted["rainfall"])
        
    if "ph" in extracted and isinstance(extracted["ph"], (int, float)):
        if 0.0 <= extracted["ph"] <= 14.0:
            validated["ph"] = float(extracted["ph"])
            
    if "land_use" in extracted and isinstance(extracted["land_use"], str):
        lu = extracted["land_use"].lower()
        if lu in VALID_LAND_USES:
            validated["land_use"] = lu
            
    if "slope_percent" in extracted and isinstance(extracted["slope_percent"], (int, float)):
        validated["slope_percent"] = float(extracted["slope_percent"])
        
    if "has_water_body" in extracted:
        validated["has_water_body"] = bool(extracted["has_water_body"])
        
    if "goal" in extracted and isinstance(extracted["goal"], str):
        validated["goal"] = extracted["goal"].lower()
        
    return validated

def get_missing_slots(state: Dict[str, Any]) -> List[str]:
    """Returns a list of required slots that are missing from the state."""
    missing = []
    for slot in REQUIRED_SLOTS:
        if slot not in state or state[slot] is None:
            missing.append(slot)
    return missing
