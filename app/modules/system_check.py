import requests


def check_ollama_status():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_ollama_models():
    """Fetch available models from local Ollama instance"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = {}
            for model in data.get('models', []):
                name = model['name']
                # Simple logic to determine "mode" for UI badging
                # Larger models = performance, Smaller = speed
                mode = 'performance' if '70b' in name or 'large' in name else 'speed'

                models[name] = {
                    'name': name,
                    'mode': mode
                }
            return models
    except Exception as e:
        print(f"⚠️ Error fetching models from Ollama: {e}")

    # Fallback if API fails but server is up
    return {
        "llama3.2:latest": {"name": "Llama 3.2 (Fallback)", "mode": "speed"}
    }