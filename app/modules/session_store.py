import threading
from typing import Dict, Any


class SessionStore:
    """Thread-safe in-memory store for session data (replaces st.session_state)"""

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str, key: str, default=None):
        with self._lock:
            if session_id not in self._store:
                return default
            return self._store[session_id].get(key, default)

    def set(self, session_id: str, key: str, value: Any):
        with self._lock:
            if session_id not in self._store:
                self._store[session_id] = {}
            self._store[session_id][key] = value

    def clear(self, session_id: str):
        with self._lock:
            if session_id in self._store:
                # Note: vectordb objects might need explicit cleanup
                self._store.pop(session_id, None)


# Global instance
store = SessionStore()