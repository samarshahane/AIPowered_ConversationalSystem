import json
import requests
from src.config import settings

def call_llm_json(prompt: str, schema_description: str) -> dict:
    """
    Calls a local Ollama instance (e.g., Llama 3) to return JSON.
    """
    # Configure your local model name here (e.g., 'llama3', 'mistral', 'phi3')
    model_name = "llama3"
    ollama_url = "http://localhost:11434/api/generate"
    
    # We append the schema instruction firmly so the local model knows exactly what to do.
    system_instruction = f"You are a strict data extraction and synthesis assistant. Always output your response in valid JSON matching this description: {schema_description}"
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": system_instruction,
        "format": "json",
        "stream": False
    }
    
    try:
        response = requests.post(ollama_url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        
        # Ollama returns the generated text in the 'response' key
        result_text = data.get("response", "{}")
        
        # Parse the string into a python dictionary/list
        return json.loads(result_text)
        
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        print("Make sure Ollama is installed and running (e.g., 'ollama serve' or 'ollama run llama3')")
        raise
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON from Ollama: {e}")
        print(f"Raw output: {result_text}")
        raise
