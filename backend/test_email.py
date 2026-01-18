"""Test email sending with Resend"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from app.auth.email_service import send_verification_email

# Load environment variables
load_dotenv()

print("Testing Resend email sending...")
print(f"API Key configured: {bool(os.getenv('RESEND_API_KEY'))}")
api_key = os.getenv('RESEND_API_KEY', '')
if api_key:
    print(f"API Key starts with: {api_key[:10]}...")

test_email = "your-email@example.com"  # Change this
test_token = "test_token_12345"

print(f"\nSending verification email to: {test_email}")
result = send_verification_email(
    to_email=test_email,
    verification_token=test_token,
    user_name="Test User"
)

if result:
    print("✅ Email operation completed!")
    print(f"Verification link: http://localhost:3001/auth/verify-email?token={test_token}")
else:
    print("❌ Email sending failed!")
