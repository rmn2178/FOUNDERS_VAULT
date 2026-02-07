#!/usr/bin/env python3
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print("🛡️  Starting Founder's Vault Flask Server...")
    print("📡 WebSocket support enabled for real-time streaming")
    print("🌐 Open http://localhost:5000 in your browser")

    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False,
        allow_unsafe_werkzeug=True    # Required for development server
    )