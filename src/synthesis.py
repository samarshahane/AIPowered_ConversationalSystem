import json
from typing import List, Dict, Any
from src.llm import call_llm_json

def synthesize_recommendations(passed_cards: List[Dict[str, Any]], retrieved_evidence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Builds the prompt from the passed cards plus retrieved evidence chunks.
    Instructs the model to explain rather than decide.
    Parses the result into the locked response schema.
    """
    if not passed_cards:
        return []

    evidence_text = "\n\n".join([
        f"Source: {e.get('metadata', {}).get('source_id')} - Page {e.get('metadata', {}).get('page')}\n{e['text']}" 
        for e in retrieved_evidence
    ])
    
    cards_text = "\n".join([f"- {c['name']}: {c['description']}" for c in passed_cards])
    card_names = [c['name'] for c in passed_cards]

    prompt = f"""
You are an environmental scientist. The system has ALREADY DETERMINED that the following interventions are feasible and optimal based on hard deterministic rules:
{cards_text}

You must write a scientific explanation for each of these selected interventions, grounded ONLY in the retrieved source passages below. 
Explain what to do, why it works scientifically, and which metrics improve. 
DO NOT decide if they are feasible. DO NOT invent numbers. If the evidence does not provide a specific number, do not include one.

Retrieved Evidence:
{evidence_text}

Return a JSON array where each object has:
- "intervention_name": string (must be one of {card_names})
- "what_to_do": string
- "scientific_explanation": string
- "metrics_improved": list of strings
- "evidence_citations": list of strings (e.g. "fao_soc_2019, Page 12")
"""
    
    schema_desc = "Array of recommendation objects."
    
    # Retry logic
    max_retries = 1
    for attempt in range(max_retries + 1):
        try:
            response = call_llm_json(prompt, schema_desc)
            if isinstance(response, list) and len(response) > 0:
                return response
            elif isinstance(response, dict) and "recommendations" in response:
                return response["recommendations"]
        except Exception as e:
            if attempt == max_retries:
                print(f"Failed to synthesize after retries: {e}")
                return [{"error": "Failed to synthesize recommendations"}]
            
    return []
