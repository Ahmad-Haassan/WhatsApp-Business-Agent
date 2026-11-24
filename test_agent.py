"""
Test suite for WhatsApp Business AI Agent
Tests:
- Webhook verification challenge
- Intent classification engine
- Calendar booking logic & meet link creation
- Simulation endpoint
"""
import sys
import os

# Add server directory to path
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server")
if server_dir not in sys.path:
    sys.path.insert(0, server_dir)

import asyncio
from services.ai_service import ai_service
from services.calendar_service import calendar_service
from services.security import verify_subscription_token
from config import settings

async def run_tests():
    print("==================================================")
    print("🧪 Running WhatsApp Business AI Agent Tests")
    print("==================================================")
    
    # 1. Test Webhook Verification
    print("\n1. Testing Webhook Verification...")
    is_valid = verify_subscription_token("subscribe", settings.WHATSAPP_VERIFY_TOKEN)
    assert is_valid, "Webhook verification token validation failed"
    is_invalid = verify_subscription_token("subscribe", "wrong_token_123")
    assert not is_invalid, "Webhook verification should reject invalid tokens"
    print("   ✅ Webhook security handshake passed")

    # 2. Test Intent Classification
    print("\n2. Testing Intent Classification...")
    test_cases = [
        ("Hi there, good morning!", "GREETING"),
        ("What are your prices and packages?", "PRICING_INQUIRY"),
        ("What services do you offer?", "SERVICES_INQUIRY"),
        ("Can we book a meeting tomorrow at 3pm?", "BOOKING_REQUEST"),
        ("What are your business hours?", "BUSINESS_INFO"),
        ("I need to speak to a human representative", "HUMAN_HANDOFF"),
    ]
    for prompt, expected_intent in test_cases:
        detected = ai_service.classify_intent(prompt)
        assert detected == expected_intent, f"Expected {expected_intent} for '{prompt}', got {detected}"
        print(f"   ✅ '{prompt}' -> {detected}")

    # 3. Test Response Generation & Interactive Buttons
    print("\n3. Testing Greeting & Interactive Buttons...")
    greeting_resp = await ai_service.generate_response("+15551234567", "Sarah", "Hello")
    assert greeting_resp["type"] == "interactive_buttons"
    assert len(greeting_resp["buttons"]) >= 2
    print(f"   ✅ Greeting generated with {len(greeting_resp['buttons'])} buttons: {[b['title'] for b in greeting_resp['buttons']]}")

    # 4. Test Calendar Booking & Meet Link Generation
    print("\n4. Testing Autonomous Calendar Scheduling...")
    booking_resp = await ai_service.generate_response(
        "+15551234567", "David", "Can we schedule a consultation call tomorrow at 4pm?"
    )
    assert booking_resp["intent"] == "BOOKING_REQUEST"
    assert "calendar_event" in booking_resp
    event = booking_resp["calendar_event"]
    assert "meet_link" in event
    assert "meet.google.com" in event["meet_link"]
    print(f"   ✅ Scheduled slot: {event['formatted_time']}")
    print(f"   ✅ Meet link created: {event['meet_link']}")

    print("\n==================================================")
    print("🎉 All 4 Test Suites Passed Successfully (100%)!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
