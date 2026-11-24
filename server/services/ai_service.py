import re
import logging
import warnings
from typing import Dict, Any, List
from config import settings
from services.calendar_service import calendar_service

logger = logging.getLogger("ai_service")

# Try modern google-genai first, then fallback to google-generativeai
HAS_MODERN_GENAI = False
HAS_LEGACY_GENAI = False

try:
    from google import genai
    HAS_MODERN_GENAI = True
except ImportError:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            import google.generativeai as legacy_genai
        HAS_LEGACY_GENAI = True
    except ImportError:
        pass

class AIService:
    def __init__(self):
        self.client = None
        self.legacy_model = None
        self._init_gemini()

    def _init_gemini(self):
        if not settings.GEMINI_API_KEY:
            return
            
        if HAS_MODERN_GENAI:
            try:
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info("Modern Google GenAI client initialized.")
                return
            except Exception as e:
                logger.warning(f"Failed to initialize modern GenAI client: {e}")
                
        if HAS_LEGACY_GENAI:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=FutureWarning)
                    legacy_genai.configure(api_key=settings.GEMINI_API_KEY)
                    self.legacy_model = legacy_genai.GenerativeModel("gemini-1.5-flash")
                logger.info("Legacy Gemini AI model initialized.")
            except Exception as e:
                logger.warning(f"Failed to initialize legacy Gemini model: {e}")

    def classify_intent(self, text: str) -> str:
        t = text.lower().strip()
        
        # Human agent handoff
        if any(k in t for k in ["human", "agent", "real person", "operator", "speak to someone", "representative"]):
            return "HUMAN_HANDOFF"
            
        # Booking / Appointment
        if any(k in t for k in ["book", "schedule", "meeting", "call", "appointment", "demo", "calendar", "consultation", "tomorrow at", "today at"]):
            return "BOOKING_REQUEST"
            
        # Pricing
        if any(k in t for k in ["price", "pricing", "cost", "how much", "rate", "fee", "package", "quote"]):
            return "PRICING_INQUIRY"
            
        # Business hours / location / contact
        if any(k in t for k in ["hour", "hours", "timing", "open", "location", "address", "where are you", "office"]):
            return "BUSINESS_INFO"
            
        # Services
        if any(k in t for k in ["service", "services", "what do you do", "offer", "help me with", "features"]):
            return "SERVICES_INQUIRY"
            
        # Greeting
        if any(re.match(rf"^{k}\b", t) for k in ["hi", "hello", "hey", "salam", "aoa", "good morning", "good evening", "hola"]):
            return "GREETING"
            
        return "GENERAL_QUERY"

    async def generate_response(
        self,
        customer_phone: str,
        customer_name: str,
        message_text: str
    ) -> Dict[str, Any]:
        """
        Processes incoming message, determines intent, performs actions
        (like scheduling if requested), and formats the appropriate response.
        """
        intent = self.classify_intent(message_text)
        logger.info(f"Classified intent for '{message_text}': {intent}")
        
        name_str = f" {customer_name}" if customer_name else ""
        
        # 1. GREETING
        if intent == "GREETING":
            return {
                "intent": intent,
                "type": "interactive_buttons",
                "message": (
                    f"Hello{name_str}! 👋 Welcome to *{settings.BUSINESS_NAME}*.\n\n"
                    "I am your virtual assistant. How can I help you today?"
                ),
                "buttons": [
                    {"id": "btn_services", "title": "💼 Our Services"},
                    {"id": "btn_pricing", "title": "💰 Pricing Plans"},
                    {"id": "btn_booking", "title": "📅 Book a Call"}
                ]
            }

        # 2. PRICING INQUIRY
        if intent == "PRICING_INQUIRY":
            return {
                "intent": intent,
                "type": "interactive_buttons",
                "message": (
                    f"Here is an overview of our current pricing at *{settings.BUSINESS_NAME}*:\n\n"
                    f"📌 {settings.BUSINESS_PRICING}\n\n"
                    "All projects include dedicated support and setup. Would you like to schedule a 15-min discovery call?"
                ),
                "buttons": [
                    {"id": "btn_booking", "title": "📅 Book Discovery"},
                    {"id": "btn_human", "title": "👤 Speak to Human"}
                ]
            }

        # 3. SERVICES INQUIRY
        if intent == "SERVICES_INQUIRY":
            return {
                "intent": intent,
                "type": "interactive_buttons",
                "message": (
                    f"At *{settings.BUSINESS_NAME}*, we specialize in:\n\n"
                    f"✨ {settings.BUSINESS_SERVICES}\n\n"
                    "We tailor solutions to fit your exact business workflows."
                ),
                "buttons": [
                    {"id": "btn_pricing", "title": "💰 View Pricing"},
                    {"id": "btn_booking", "title": "📅 Schedule Demo"}
                ]
            }

        # 4. BUSINESS INFO & HOURS
        if intent == "BUSINESS_INFO":
            return {
                "intent": intent,
                "type": "text",
                "message": (
                    f"🏢 *{settings.BUSINESS_NAME}* Information:\n\n"
                    f"🕒 *Business Hours*: {settings.BUSINESS_HOURS}\n"
                    "📍 *Service Availability*: Remote Global Delivery & Cloud Consulting\n"
                    "📧 *Email*: contact@ahmad-solutions.com\n\n"
                    "Feel free to ask any question or book an appointment anytime!"
                )
            }

        # 5. BOOKING REQUEST
        if intent == "BOOKING_REQUEST":
            booking = await calendar_service.schedule_appointment(
                customer_phone=customer_phone,
                customer_name=customer_name,
                requested_text=message_text
            )
            return {
                "intent": intent,
                "type": "text",
                "calendar_event": booking,
                "message": (
                    f"✅ *Appointment Confirmed!*{name_str}\n\n"
                    f"📅 *Date & Time*: {booking['formatted_time']}\n"
                    f"🔗 *Google Meet Link*: {booking['meet_link']}\n\n"
                    "A calendar invitation has been prepared. We look forward to speaking with you!"
                )
            }

        # 6. HUMAN HANDOFF
        if intent == "HUMAN_HANDOFF":
            return {
                "intent": intent,
                "type": "text",
                "message": (
                    f"Got it{name_str}! 🔔 I have notified a human representative from *{settings.BUSINESS_NAME}*.\n\n"
                    "Someone will take over this chat shortly during business hours. Thank you for your patience!"
                )
            }

        # 7. GENERAL QUERY (Gemini AI or Contextual Fallback)
        system_context = (
            f"You are the official WhatsApp Business AI Assistant for {settings.BUSINESS_NAME}. "
            f"Services offered: {settings.BUSINESS_SERVICES}. "
            f"Pricing details: {settings.BUSINESS_PRICING}. "
            f"Operating hours: {settings.BUSINESS_HOURS}. "
            "Keep answers concise, professional, friendly, and formatted for WhatsApp (bold key terms with *asterisks*)."
        )

        if self.client:
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"{system_context}\n\nCustomer: {message_text}\nAssistant:"
                )
                if response and response.text:
                    return {
                        "intent": "GENERAL_QUERY",
                        "type": "text",
                        "message": response.text.strip()
                    }
            except Exception as e:
                logger.error(f"GenAI Client generation error: {e}")

        elif self.legacy_model:
            try:
                prompt = f"{system_context}\n\nCustomer: {message_text}\nAssistant:"
                response = self.legacy_model.generate_content(prompt)
                if response and response.text:
                    return {
                        "intent": "GENERAL_QUERY",
                        "type": "text",
                        "message": response.text.strip()
                    }
            except Exception as e:
                logger.error(f"Legacy Gemini API generation error: {e}")

        # Default Fallback
        return {
            "intent": "GENERAL_QUERY",
            "type": "interactive_buttons",
            "message": (
                f"Thank you for contacting *{settings.BUSINESS_NAME}*! "
                "I can answer questions regarding our services, share pricing, or book a consultation call."
            ),
            "buttons": [
                {"id": "btn_services", "title": "💼 Services"},
                {"id": "btn_pricing", "title": "💰 Pricing"},
                {"id": "btn_booking", "title": "📅 Book Call"}
            ]
        }

ai_service = AIService()
