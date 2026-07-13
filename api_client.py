import requests

# --- API Keys Configuration ---
# You will replace these strings with your actual API keys later
OPENROUTER_API_KEY = "your_openrouter_api_key_here"
NVIDIA_API_KEY = "your_nvidia_api_key_here"

def get_ai_response(messages, model, provider="openrouter"):
    """
    Sends the chat history to the selected AI provider and returns the response.
    'messages' should be a list of dictionaries, e.g., [{"role": "user", "content": "Hello!"}]
    """
    if provider == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost", # Recommended by OpenRouter
            "X-Title": "ALANX Workspace",
            "Content-Type": "application/json"
        }
    elif provider == "nvidia":
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }
    else:
        return "Error: Unknown AI provider selected."

    # The payload structure is identical for both!
    payload = {
        "model": model,
        "messages": messages,
        "stream": False # We can enable streaming later for typing effects
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Raises an error for bad HTTP status codes
        
        data = response.json()
        return data['choices'][0]['message']['content']
        
    except requests.exceptions.RequestException as e:
        return f"Network or API Error: {str(e)}"
    except KeyError:
        return "Error: Unexpected response format from the API."

# --- Quick Test (Optional) ---
if __name__ == "__main__":
    print("API Client initialized. Ready to send requests once keys are added.")