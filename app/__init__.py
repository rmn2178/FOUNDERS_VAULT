from flask import Flask
from flask_socketio import SocketIO
from config import Config
import os
import uuid

# Import the fixed session interface
from app.utils.session_fix import FixedFileSystemSessionInterface

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['CHROMA_DB_PATH'], exist_ok=True)
    session_dir = app.config.get('SESSION_FILE_DIR', 'flask_session')
    os.makedirs(session_dir, exist_ok=True)

    # Use fixed session interface instead of default Flask-Session
    app.session_interface = FixedFileSystemSessionInterface(
        cache_dir=session_dir,
        threshold=app.config.get('SESSION_FILE_THRESHOLD', 500),
        mode=app.config.get('SESSION_FILE_MODE', 384),
        key_prefix=app.config.get('SESSION_KEY_PREFIX', 'session:')
    )

    # Ensure session ID is string on each request
    @app.before_request
    def ensure_string_session():
        from flask import session
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        elif isinstance(session.get('session_id'), bytes):
            session['session_id'] = session['session_id'].decode('utf-8')

    socketio.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app