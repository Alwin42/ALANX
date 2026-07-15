import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

def get_ai_response(messages, model, provider="openrouter"):
    if provider == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "ALANX Workspace",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "reasoning": {"enabled": True}  # Enable chain-of-thought for OpenRouter
        }
    elif provider == "nvidia":
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
    else:
        return {"content": "Error: Unknown AI provider selected.", "reasoning_details": None}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        message_data = data['choices'][0]['message']
        return {
            "content": message_data.get("content", ""),
            "reasoning_details": message_data.get("reasoning_details", None)
        }
        
    except Exception as e:
        return {"content": f"Network or API Error: {str(e)}", "reasoning_details": None}