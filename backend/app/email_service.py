"""
Email notification service for sending reminder and overdue emails.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional
import os

from sqlmodel import Session, select
from app.models import User

logger = logging.getLogger(__name__)

# Email configuration from environment
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
APP_NAME = "FlowTask"


def send_email(to_email: str, subject: str, html_body: str, text_body: str) -> bool:
    """
    Send an email using Gmail SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML version of email body
        text_body: Plain text version of email body

    Returns:
        True if email sent successfully, False otherwise
    """
    # Skip if SMTP not configured
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured, skipping email send")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"FlowTask App <{FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach parts
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Send via SMTP
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_reminder_email(user_id: int, task_title: str, due_date: Optional[datetime], session: Session) -> bool:
    """
    Send a reminder email for an upcoming task.

    Args:
        user_id: User ID
        task_title: Task title
        due_date: Task due date
        session: Database session

    Returns:
        True if email sent successfully
    """
    # Get user email
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user or not user.email:
        logger.warning(f"No email found for user {user_id}")
        return False

    # Format due date
    due_str = due_date.strftime("%B %d, %Y at %I:%M %p") if due_date else "soon"

    # Email subject
    subject = f"⏰ Reminder: {task_title}"

    # Plain text body
    text_body = f"""
Hello,

This is a reminder that your task "{task_title}" is due {due_str}.

View your task at: http://localhost:3001/dashboard

Best regards,
{APP_NAME}
    """.strip()

    # HTML body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
            .task-title {{ font-size: 20px; font-weight: bold; color: #1f2937; margin: 15px 0; }}
            .due-date {{ font-size: 16px; color: #6b7280; margin: 10px 0; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #3b82f6; color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #9ca3af; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⏰ Task Reminder</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>This is a reminder that your task is coming up:</p>
                <div class="task-title">"{task_title}"</div>
                <div class="due-date">📅 Due: {due_str}</div>
                <a href="http://localhost:3001/dashboard" class="button">View Task</a>
            </div>
            <div class="footer">
                <p>You're receiving this because you set a reminder for this task.</p>
                <p>{APP_NAME}</p>
            </div>
        </div>
    </body>
    </html>
    """.strip()

    return send_email(user.email, subject, html_body, text_body)


def send_overdue_email(user_id: int, task_title: str, due_date: Optional[datetime], session: Session) -> bool:
    """
    Send an overdue notification email for a past-due task.

    Args:
        user_id: User ID
        task_title: Task title
        due_date: Task due date (in the past)
        session: Database session

    Returns:
        True if email sent successfully
    """
    # Get user email
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user or not user.email:
        logger.warning(f"No email found for user {user_id}")
        return False

    # Format due date
    due_str = due_date.strftime("%B %d, %Y at %I:%M %p") if due_date else "recently"

    # Email subject
    subject = f"🚨 Overdue: {task_title}"

    # Plain text body
    text_body = f"""
Hello,

Your task "{task_title}" is now overdue. It was due on {due_str}.

View your task at: http://localhost:3001/dashboard

Best regards,
{APP_NAME}
    """.strip()

    # HTML body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #ef4444; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background-color: #fef2f2; padding: 30px; border-radius: 0 0 8px 8px; }}
            .task-title {{ font-size: 20px; font-weight: bold; color: #991b1b; margin: 15px 0; }}
            .due-date {{ font-size: 16px; color: #dc2626; margin: 10px 0; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #ef4444; color: white; text-decoration: none; border-radius: 6px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #9ca3af; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚨 Task Overdue</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Your task is now overdue:</p>
                <div class="task-title">"{task_title}"</div>
                <div class="due-date">📅 Was due: {due_str}</div>
                <a href="http://localhost:3001/dashboard" class="button">View Task</a>
            </div>
            <div class="footer">
                <p>Complete this task or adjust its due date.</p>
                <p>{APP_NAME}</p>
            </div>
        </div>
    </body>
    </html>
    """.strip()

    return send_email(user.email, subject, html_body, text_body)
