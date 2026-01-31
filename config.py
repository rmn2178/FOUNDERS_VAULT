import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chroma_db')

    # Use Redis in production, filesystem in development
    SESSION_TYPE = 'filesystem'  # Change to 'redis' if Redis is available
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Available models
    MODEL_OPTIONS = {
        "llama3.2:latest": {"name": "Llama 3.2", "mode": "speed"},
        "phi4-mini:3.8b": {"name": "Phi-4 Mini", "mode": "speed"},
        "deepseek-r1:7b": {"name": "Deepseek R1 7B", "mode": "performance"},
        "qwen2.5-coder:7b-instruct-q4_K_M": {"name": "Qwen 2.5 Coder", "mode": "performance"}
    }