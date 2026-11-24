import sys
import os
import time
import json
import logging
from typing import Dict, Any, Optional

# Ensure server directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, JSONResponse
import socketio

from config import settings
from services.security import verify_subscription_token, verify_meta_signature
from services.whatsapp_service import whatsapp_service, activity_logs, record_activity
from services.ai_service import ai_service
from services.calendar_service import calendar_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("wauto-server")

# Initialize Socket.IO for real-time dashboard events
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = FastAPI(
    title="WhatsApp Business AI Agent API",
    description="Webhook gateway, AI intent classification, and Google Calendar scheduler",
    version="1.0.0"
)

# Enable CORS for local client and web preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Combined ASGI app for uvicorn (uvicorn main:socket_app)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

SERVER_START_TIME = time.time()

@sio.event
async def connect(sid, environ):
    logger.info(f"Dashboard client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Dashboard client disconnected: {sid}")

@app.get("/")
async def root():
    return {
        "service": "WhatsApp Business AI Agent",
        "status": "online",
        "uptime_seconds": int(time.time() - SERVER_START_TIME),
        "docs_url": "/docs",
        "meta_webhook_url": "/webhook",
        "simulator_url": "/api/simulate"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Handles Meta's Webhook Verification Challenge (GET request).
    Meta documentation: https://developers.facebook.com/docs/graph-api/webhooks/getting-started
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if verify_subscription_token(mode, token):
            logger.info("Meta Webhook verification handshake successful!")
            return PlainTextResponse(content=challenge, status_code=status.HTTP_200_OK)
        else:
            logger.warning(f"Webhook verification failed with token: '{token}'")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")
            
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing hub parameters")

@app.post("/webhook")
async def receive_webhook(request: Request):
    """
    Receives incoming webhook events from Meta Cloud API.
    """
    body_bytes = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    # Security check
    if not verify_meta_signature(body_bytes, signature):
        logger.warning("Invalid Meta signature detected on incoming webhook!")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception as e:
        logger.error(f"Malformed JSON payload received: {e}")
        return JSONResponse({"status": "ignored", "error": "invalid_json"}, status_code=200)

    # Process Meta WhatsApp payload structure
    entries = payload.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            contacts = {c.get("wa_id"): c.get("profile", {}).get("name") for c in value.get("contacts", [])}
            messages = value.get("messages", [])

            for msg in messages:
                sender_phone = msg.get("from")
                msg_id = msg.get("id")
                msg_type = msg.get("type")
                customer_name = contacts.get(sender_phone, "Customer")

                # Extract text content (either direct text or quick reply button)
                text_content = ""
                if msg_type == "text":
                    text_content = msg.get("text", {}).get("body", "")
                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    button_reply = interactive.get("button_reply", {})
                    text_content = button_reply.get("title", "") or button_reply.get("id", "")

                if not text_content:
                    continue

                logger.info(f"Incoming message from {sender_phone} ({customer_name}): '{text_content}'")
                
                # Record inbound message
                inbound_entry = record_activity(
                    "inbound", sender_phone, text_content,
                    {"customer_name": customer_name, "message_id": msg_id, "type": msg_type}
                )
                await sio.emit("message_received", inbound_entry)

                # Mark as read
                await whatsapp_service.mark_as_read(msg_id)

                # Process with AI intent engine
                ai_result = await ai_service.generate_response(sender_phone, customer_name, text_content)

                # Send outbound reply via Meta Cloud API
                if ai_result.get("type") == "interactive_buttons" and ai_result.get("buttons"):
                    await whatsapp_service.send_interactive_buttons(
                        to=sender_phone,
                        body_text=ai_result["message"],
                        buttons=ai_result["buttons"]
                    )
                else:
                    await whatsapp_service.send_text_message(
                        to=sender_phone,
                        text=ai_result["message"]
                    )

                # Broadcast outbound reply to dashboard
                await sio.emit("message_sent", {
                    "to": sender_phone,
                    "response": ai_result
                })

    return JSONResponse(content={"status": "EVENT_RECEIVED"}, status_code=200)

@app.post("/api/simulate")
async def simulate_message(data: Dict[str, Any]):
    """
    Simulation endpoint for testing the conversational agent locally
    without needing a live Meta WhatsApp Business account.
    """
    phone = data.get("phone", "+1234567890")
    name = data.get("name", "Test User")
    message = data.get("message", "Hello")

    inbound_entry = record_activity("inbound", phone, message, {"customer_name": name, "simulation": True})
    await sio.emit("message_received", inbound_entry)

    # Run intent & AI reasoning engine
    ai_result = await ai_service.generate_response(phone, name, message)

    # Record simulated outbound activity
    outbound_entry = record_activity(
        "outbound", phone, ai_result["message"],
        {"intent": ai_result.get("intent"), "type": ai_result.get("type"), "simulation": True}
    )
    await sio.emit("message_sent", outbound_entry)

    return {
        "status": "success",
        "customer": {"phone": phone, "name": name, "input": message},
        "agent_response": ai_result,
        "is_configured": whatsapp_service.is_configured
    }

@app.get("/api/logs")
async def get_logs():
    return {"logs": activity_logs}

@app.get("/api/status")
async def get_system_status():
    return {
        "server": "online",
        "uptime": int(time.time() - SERVER_START_TIME),
        "whatsapp_configured": whatsapp_service.is_configured,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "calendar_configured": calendar_service.is_configured,
        "verify_token": settings.WHATSAPP_VERIFY_TOKEN,
        "business_name": settings.BUSINESS_NAME,
        "business_hours": settings.BUSINESS_HOURS
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:socket_app", host=settings.HOST, port=settings.PORT, reload=True)
