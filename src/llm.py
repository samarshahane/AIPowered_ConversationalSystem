import json
import os
import requests
from src.config import settings

def call_llm_json(prompt: str, schema_description: str) -> dict:
    """
    Calls configured LLM provider (Groq, Gemini, or Ollama) and returns parsed JSON.
    """
    provider = settings.llm_provider.lower()

    if provider == "groq":
        return _call_groq(prompt, schema_description)
    elif provider == "gemini":
        return _call_gemini(prompt, schema_description)
    else:
        return _call_ollama(prompt, schema_description)

def _call_ollama(prompt: str, schema_description: str) -> dict:
    model_name = os.getenv("OLLAMA_MODEL", "llama3")
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    system_instruction = f"You are a strict data extraction and synthesis assistant. Always output your response in valid JSON matching this description: {schema_description}"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": system_instruction,
        "format": "json",
        "stream": False
    }
    response = requests.post(ollama_url, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    result_text = data.get("response", "{}")
    return json.loads(result_text)

def _call_gemini(prompt: str, schema_description: str) -> dict:
    api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    full_prompt = (
        f"You must return ONLY valid JSON (no markdown fences, no extra text).\n"
        f"Schema requirement: {schema_description}\n\n"
        f"Task:\n{prompt}"
    )
    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2
        }
    }
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    raw_text = result["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(raw_text)

def _call_groq(prompt: str, schema_description: str) -> dict:
    api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing.")

    model = settings.groq_model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_instruction = (
        f"You are a strict data extraction and synthesis assistant. "
        f"Always output your response in valid JSON matching this schema/description: {schema_description}. "
        f"Output ONLY raw JSON, no markdown codeblocks, no explanations."
    )
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.2
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    result_text = data["choices"][0]["message"]["content"]
    return json.loads(result_text)
