import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file from server dir or root dir
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

class Settings(BaseSettings):
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Meta WhatsApp Cloud API credentials
    WHATSAPP_PHONE_NUMBER_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "wauto_verify_token_dev")
    WHATSAPP_APP_SECRET: str = os.getenv("WHATSAPP_APP_SECRET", "")
    
    # Google Gemini AI credentials
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("AI_API_KEY", ""))
    
    # Google Calendar credentials
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    
    # Business Knowledge Defaults
    BUSINESS_NAME: str = os.getenv("BUSINESS_NAME", "Ahmad Tech Solutions")
    BUSINESS_HOURS: str = os.getenv("BUSINESS_HOURS", "Mon - Fri: 9:00 AM - 6:00 PM EST")
    BUSINESS_SERVICES: str = os.getenv(
        "BUSINESS_SERVICES",
        "AI Agents, Custom Web/Mobile Development, WhatsApp Automation, Cloud Architecture"
    )
    BUSINESS_PRICING: str = os.getenv(
        "BUSINESS_PRICING",
        "Starter Automation Package: $500 | Custom Agent Build: $1,200 | Enterprise Retainer: $2,500/mo"
    )

settings = Settings()
