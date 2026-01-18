"""Test email sending"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

import resend

# Check API key
api_key = os.getenv("RESEND_API_KEY", "")
print("=== RESEND EMAIL TEST ===")
print(f"API Key configured: {bool(api_key)}")
print(f"API Key length: {len(api_key)}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")

# Set API key
resend.api_key = api_key

# Test send
print("\nAttempting to send test email...")
test_email = "nauman.khalid@example.com"

try:
    response = resend.Emails.send({
        "from": "FlowTask <onboarding@resend.dev>",
        "to": test_email,
        "subject": "Test Email from FlowTask",
        "html": "<h1>Test Email</h1><p>If you received this, email delivery is working!</p>"
    })
    print(f"SUCCESS! Email sent.")
    print(f"Response: {response}")
except Exception as e:
    print(f"ERROR: {e}")
    print(f"Error type: {type(e).__name__}")
