"""Email service using Resend"""
import os
from typing import Optional
import resend

# Configure Resend API key
resend.api_key = os.getenv("RESEND_API_KEY", "")

def send_verification_email(to_email: str, verification_token: str, user_name: Optional[str] = None) -> bool:
    """Send email verification email using Resend"""
    # Check if API key is properly configured (not placeholder)
    is_valid_key = resend.api_key and not resend.api_key.startswith('re_123456789')

    # Use FRONTEND_URL from environment or default to todo.local
    frontend_url = os.getenv("FRONTEND_URL", "http://todo.local")

    if not is_valid_key:
        print("\n" + "="*80)
        print(f"[EMAIL] Verification email for: {to_email}")
        print(f"[LINK]  {frontend_url}/auth/verify-email?token={verification_token}")
        print("="*80 + "\n")
        return True  # Return True in development mode

    display_name = user_name or to_email.split('@')[0]
    verification_url = f"{frontend_url}/auth/verify-email?token={verification_token}"

    try:
        resend.Emails.send({
            "from": "FlowTask <onboarding@resend.dev>",
            "to": to_email,
            "subject": "✓ Verify your FlowTask account",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0; font-size: 32px;">✓ FlowTask</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Effortless Productivity, Beautiful Design</p>
                    </div>
                    <div class="content">
                        <h2>Welcome to FlowTask, {display_name}!</h2>
                        <p>Thanks for signing up. You're one step away from transforming your productivity.</p>
                        <p>Click the button below to verify your email and activate your account:</p>
                        <div style="text-align: center;">
                            <a href="{verification_url}" class="button">Verify Email Address</a>
                        </div>
                        <p style="color: #6b7280; font-size: 14px;">Or copy and paste this link into your browser:</p>
                        <p style="background: white; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 12px;">{verification_url}</p>
                        <p style="margin-top: 30px; color: #6b7280; font-size: 14px;">This link will expire in 24 hours.</p>
                    </div>
                    <div class="footer">
                        <p>Powered by <strong>Nauman Khalid</strong></p>
                        <p>&copy; 2025 FlowTask. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        })
        print(f"[EMAIL] Verification email sent successfully to: {to_email}")
        return True
    except Exception as e:
        frontend_url = os.getenv("FRONTEND_URL", "http://todo.local")
        print(f"\n[ERROR] Failed to send email: {e}")
        print(f"[EMAIL] Verification email for: {to_email}")
        print(f"[LINK]  {frontend_url}/auth/verify-email?token={verification_token}")
        print("="*80 + "\n")
        return False


def send_welcome_email(to_email: str, user_name: Optional[str] = None) -> bool:
    """Send welcome email after verification"""
    # Check if API key is properly configured (not placeholder)
    is_valid_key = resend.api_key and not resend.api_key.startswith('re_123456789')

    # Use FRONTEND_URL from environment or default to todo.local
    frontend_url = os.getenv("FRONTEND_URL", "http://todo.local")

    if not is_valid_key:
        print(f"\n[EMAIL] Welcome email would be sent to: {to_email}\n")
        return True

    display_name = user_name or to_email.split('@')[0]

    try:
        resend.Emails.send({
            "from": "FlowTask <onboarding@resend.dev>",
            "to": to_email,
            "subject": "🎉 Welcome to FlowTask!",
            "html": f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0; font-size: 32px;">🎉 You're All Set!</h1>
                    </div>
                    <div class="content">
                        <h2>Welcome aboard, {display_name}!</h2>
                        <p>Your FlowTask account is now active. Here's what you can do:</p>

                        <div class="feature">
                            <strong>🎯 Smart Organization</strong>
                            <p style="margin: 5px 0 0 0;">Priorities, tags, advanced filtering, and instant search</p>
                        </div>

                        <div class="feature">
                            <strong>✨ 3D Visual Effects</strong>
                            <p style="margin: 5px 0 0 0;">Stunning glassmorphism with 60fps animations</p>
                        </div>

                        <div class="feature">
                            <strong>🌙 Perfect Dark Mode</strong>
                            <p style="margin: 5px 0 0 0;">Flicker-free themes with system detection</p>
                        </div>

                        <div style="text-align: center;">
                            <a href="{frontend_url}/dashboard" class="button">Go to Dashboard</a>
                        </div>
                    </div>
                    <div style="text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px;">
                        <p>Powered by <strong>Nauman Khalid</strong></p>
                        <p>&copy; 2025 FlowTask. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        })
        print(f"[EMAIL] Welcome email sent successfully to: {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send welcome email: {e}")
        print(f"[EMAIL] Welcome email would be sent to: {to_email}")
        return False
