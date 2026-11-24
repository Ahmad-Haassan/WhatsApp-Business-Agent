import sys
import os

# Add server directory to path
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server")
if server_dir not in sys.path:
    sys.path.insert(0, server_dir)

import uvicorn
from config import settings

if __name__ == "__main__":
    print("=======================================================")
    print("🤖 Starting WhatsApp Business AI Agent Server...")
    print(f"📡 Host: {settings.HOST}:{settings.PORT}")
    print(f"🔗 Webhook Endpoint: http://localhost:{settings.PORT}/webhook")
    print(f"🧪 Simulator Endpoint: http://localhost:{settings.PORT}/api/simulate")
    print("=======================================================")
    uvicorn.run("main:socket_app", host=settings.HOST, port=settings.PORT, app_dir=server_dir, reload=True)
