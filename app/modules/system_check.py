import requests

def check_ollama_status():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/", timeout=2)
        return response.status_code == 200
    except:
        return False