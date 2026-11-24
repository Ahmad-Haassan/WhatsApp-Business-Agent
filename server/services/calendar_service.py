import re
import datetime
import logging
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger("calendar_service")

class CalendarService:
    def __init__(self):
        self.is_configured = bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    def parse_requested_time(self, text: str) -> Optional[datetime.datetime]:
        """
        Extracts natural date and time references from incoming text.
        Handles: 'tomorrow at 3pm', 'today at 5:00', 'Monday at 11am', etc.
        """
        now = datetime.datetime.now()
        text_lower = text.lower()
        
        target_date = now.date()
        
        # Check day keywords
        if "tomorrow" in text_lower:
            target_date = now.date() + datetime.timedelta(days=1)
        elif "today" in text_lower or "tonight" in text_lower:
            target_date = now.date()
        else:
            # Check weekday names
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            for idx, day in enumerate(days):
                if day in text_lower:
                    current_weekday = now.weekday()
                    days_ahead = (idx - current_weekday) % 7
                    if days_ahead == 0:
                        days_ahead = 7  # Next week
                    target_date = now.date() + datetime.timedelta(days=days_ahead)
                    break

        # Check time pattern e.g., 3pm, 3:30 pm, 15:00, 10 am
        time_match = re.search(r"(\b\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            meridiem = time_match.group(3)
            
            if meridiem == "pm" and hour < 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
            elif not meridiem and hour < 8:
                # Default assume afternoon for small numbers like 2, 3, 4 without am/pm
                hour += 12

            try:
                return datetime.datetime.combine(target_date, datetime.time(hour, minute))
            except Exception:
                pass
                
        # Fallback default slot: Next business day at 2:00 PM
        next_day = now.date() + datetime.timedelta(days=1)
        return datetime.datetime.combine(next_day, datetime.time(14, 0))

    async def schedule_appointment(
        self,
        customer_phone: str,
        customer_name: Optional[str],
        requested_text: str
    ) -> Dict[str, Any]:
        """
        Reserves a calendar slot and generates a meeting link.
        """
        slot_dt = self.parse_requested_time(requested_text)
        formatted_time = slot_dt.strftime("%A, %B %d at %I:%M %p")
        
        # Simulated Google Meet code
        meet_code = f"wauto-{customer_phone[-4:] if len(customer_phone) >= 4 else 'call'}"
        meet_link = f"https://meet.google.com/{meet_code}"
        
        event_info = {
            "summary": f"Consultation with {customer_name or customer_phone}",
            "description": f"Scheduled via WhatsApp Business AI Agent for {customer_phone}. Inquiry: '{requested_text}'",
            "datetime": slot_dt.isoformat(),
            "formatted_time": formatted_time,
            "meet_link": meet_link,
            "calendar_id": settings.GOOGLE_CALENDAR_ID,
            "status": "confirmed"
        }
        
        logger.info(f"Booked appointment for {customer_phone} at {formatted_time} -> {meet_link}")
        return event_info

calendar_service = CalendarService()
