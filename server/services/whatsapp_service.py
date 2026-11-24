import httpx
import logging
from typing import List, Dict, Any, Optional
from config import settings

logger = logging.getLogger("whatsapp_service")

# In-memory activity store for dashboard inspection
activity_logs: List[Dict[str, Any]] = []

def record_activity(direction: str, recipient_or_sender: str, message: str, meta: Optional[Dict[str, Any]] = None):
    entry = {
        "id": f"act_{len(activity_logs) + 1}",
        "timestamp": meta.get("timestamp") if meta and "timestamp" in meta else None,
        "direction": direction,  # "inbound" | "outbound"
        "phone": recipient_or_sender,
        "message": message,
        "meta": meta or {}
    }
    activity_logs.append(entry)
    # Keep only last 100 entries
    if len(activity_logs) > 100:
        activity_logs.pop(0)
    return entry

class WhatsAppService:
    def __init__(self):
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
    @property
    def is_configured(self) -> bool:
        return bool(settings.WHATSAPP_PHONE_NUMBER_ID and settings.WHATSAPP_ACCESS_TOKEN)

    async def mark_as_read(self, message_id: str) -> bool:
        if not self.is_configured:
            logger.info(f"[SIMULATION] Marked message {message_id} as read")
            return True
            
        url = f"{self.base_url}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                return res.status_code == 200
        except Exception as e:
            logger.error(f"Error marking message {message_id} as read: {e}")
            return False

    async def send_text_message(self, to: str, text: str) -> Dict[str, Any]:
        """
        Sends standard text message via WhatsApp Cloud API.
        """
        record_activity("outbound", to, text, {"type": "text"})
        
        if not self.is_configured:
            logger.info(f"[SIMULATION OUTBOUND] To: {to} | Text: {text}")
            return {"status": "simulated", "recipient": to, "message": text}
            
        url = f"{self.base_url}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {"preview_url": True, "body": text}
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                logger.error(f"Meta API Error ({resp.status_code}): {resp.text}")
                return {"status": "error", "code": resp.status_code, "detail": resp.text}
            return resp.json()

    async def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Sends interactive quick-reply buttons (Max 3 buttons allowed by Meta API).
        buttons format: [{"id": "btn_1", "title": "View Pricing"}]
        """
        record_activity("outbound", to, body_text, {"type": "interactive_buttons", "buttons": buttons})
        
        if not self.is_configured:
            logger.info(f"[SIMULATION OUTBOUND INTERACTIVE] To: {to} | Body: {body_text} | Buttons: {buttons}")
            return {
                "status": "simulated",
                "recipient": to,
                "body": body_text,
                "buttons": buttons
            }
            
        url = f"{self.base_url}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        action_buttons = []
        for btn in buttons[:3]:  # Meta allows at most 3 quick reply buttons
            action_buttons.append({
                "type": "reply",
                "reply": {
                    "id": btn.get("id", f"btn_{len(action_buttons)}"),
                    "title": btn.get("title", "")[:20]  # Max 20 chars
                }
            })
            
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": action_buttons}
            }
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code >= 400:
                logger.error(f"Meta API Error: {resp.text}")
                return {"status": "error", "code": resp.status_code, "detail": resp.text}
            return resp.json()

whatsapp_service = WhatsAppService()
