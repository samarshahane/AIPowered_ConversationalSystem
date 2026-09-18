from typing import List, Dict, Any

def build_trace(
    evaluated_cards_count: int,
    passed_cards_count: int,
    rejections: List[Dict[str, str]],
    scores: Dict[str, float],
    retrieved_chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Assembles the full trace object to be saved in the session and returned in the API.
    """
    return {
        "evaluated_cards": evaluated_cards_count,
        "passed_cards": passed_cards_count,
        "rejections": rejections,
        "scores": scores,
        "retrieved_chunks": [
            {
                "source_id": chunk.get("metadata", {}).get("source_id"),
                "page": chunk.get("metadata", {}).get("page"),
                "score": chunk.get("score"),
                "snippet": chunk.get("text", "")[:200] + "..." # Snippet for UI trace
            }
            for chunk in retrieved_chunks
        ]
    }
