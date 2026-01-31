from flask_session.sessions import FileSystemSessionInterface
import uuid


class FixedFileSystemSessionInterface(FileSystemSessionInterface):
    """Fixed session interface that ensures session IDs are strings"""

    def _generate_sid(self):
        # Always return string UUID
        return str(uuid.uuid4())

    def save_session(self, app, session, response):
        # Ensure session ID is string before saving
        if session.get('session_id') and isinstance(session['session_id'], bytes):
            session['session_id'] = session['session_id'].decode('utf-8')
        super().save_session(app, session, response)