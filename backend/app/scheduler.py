"""
Background scheduler for checking reminders and overdue tasks.

Uses APScheduler to run periodic checks every 60 seconds.
"""

import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlmodel import Session, select

from app.database import engine
from app.models import Task, Notification
from app.email_service import send_reminder_email, send_overdue_email

logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()


def check_reminders_and_overdue():
    """
    Scheduled job that runs every 60 seconds to check for:
    1. Tasks with reminder_time <= NOW() (send reminder notifications)
    2. Tasks with due_date <= NOW() and not completed (send overdue notifications)
    """
    logger.info("=== Scheduler running: Checking for reminders and overdue tasks ===")
    try:
        with Session(engine) as session:
            now = datetime.utcnow()
            logger.info(f"Current UTC time: {now}")

            # Query 1: Check for reminder notifications
            logger.info("Querying for tasks with reminder_time <= now, not sent, not completed...")
            reminder_tasks = session.exec(
                select(Task).where(
                    Task.reminder_time <= now,
                    Task.reminder_time.is_not(None),
                    Task.last_reminder_sent.is_(None),
                    Task.completed == False
                )
            ).all()
            logger.info(f"Found {len(reminder_tasks)} tasks needing reminders")

            for task in reminder_tasks:
                logger.info(f"Processing reminder for task #{task.id}: '{task.title}'")

                # Create in-app notification
                notification = Notification(
                    user_id=task.user_id,
                    task_id=task.id,
                    type="reminder",
                    title=f"Reminder: {task.title}",
                    message=f"This task is due {format_due_time(task.due_date)}",
                    is_read=False,
                    created_at=now
                )
                session.add(notification)
                logger.info(f"  ✓ Created in-app notification")

                # Send email notification
                try:
                    email_sent = send_reminder_email(
                        user_id=task.user_id,
                        task_title=task.title,
                        due_date=task.due_date,
                        session=session
                    )
                    if email_sent:
                        logger.info(f"  ✓ Sent email reminder")
                    else:
                        logger.warning(f"  ✗ Email reminder not sent (check SMTP config)")
                except Exception as e:
                    logger.error(f"Failed to send reminder email for task {task.id}: {e}")

                # Update last_reminder_sent
                task.last_reminder_sent = now
                session.add(task)
                logger.info(f"  ✓ Updated last_reminder_sent to {now}")

            # Query 2: Check for overdue notifications
            logger.info("Querying for overdue tasks (due_date <= now, not completed, not notified)...")
            overdue_tasks = session.exec(
                select(Task).where(
                    Task.due_date <= now,
                    Task.due_date.is_not(None),
                    Task.completed == False,
                    Task.last_overdue_notification_sent.is_(None)
                )
            ).all()
            logger.info(f"Found {len(overdue_tasks)} overdue tasks")

            for task in overdue_tasks:
                # Create in-app notification
                notification = Notification(
                    user_id=task.user_id,
                    task_id=task.id,
                    type="overdue",
                    title=f"Overdue: {task.title}",
                    message=f"This task was due {format_overdue_time(task.due_date)}",
                    is_read=False,
                    created_at=now
                )
                session.add(notification)

                # Send email notification
                try:
                    send_overdue_email(
                        user_id=task.user_id,
                        task_title=task.title,
                        due_date=task.due_date,
                        session=session
                    )
                except Exception as e:
                    logger.error(f"Failed to send overdue email for task {task.id}: {e}")

                # Update last_overdue_notification_sent
                task.last_overdue_notification_sent = now
                session.add(task)

            # Commit all changes
            session.commit()
            logger.info(f"✓ Committed all changes to database")

            logger.info(
                f"=== Scheduler complete: Processed {len(reminder_tasks)} reminder(s) and "
                f"{len(overdue_tasks)} overdue notification(s) ==="
            )

    except Exception as e:
        logger.error(f"Error in check_reminders_and_overdue: {e}", exc_info=True)


def format_due_time(due_date: Optional[datetime]) -> str:
    """Format due date as human-readable string"""
    if not due_date:
        return "soon"

    now = datetime.utcnow()
    diff = due_date - now

    hours = diff.total_seconds() / 3600
    if hours < 1:
        return "in less than an hour"
    elif hours < 24:
        return f"in {int(hours)} hour(s)"
    else:
        days = int(hours / 24)
        return f"in {days} day(s)"


def format_overdue_time(due_date: Optional[datetime]) -> str:
    """Format overdue time as human-readable string"""
    if not due_date:
        return "recently"

    now = datetime.utcnow()
    diff = now - due_date

    hours = diff.total_seconds() / 3600
    if hours < 1:
        return "less than an hour ago"
    elif hours < 24:
        return f"{int(hours)} hour(s) ago"
    else:
        days = int(hours / 24)
        return f"{days} day(s) ago"


def start_scheduler():
    """Initialize and start the background scheduler"""
    logger.info("Starting background scheduler...")

    # Add the scheduled job (runs every 60 seconds)
    scheduler.add_job(
        check_reminders_and_overdue,
        'interval',
        seconds=60,
        id='check_reminders',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Background scheduler started successfully")


def shutdown_scheduler():
    """Shutdown the background scheduler gracefully"""
    logger.info("Shutting down background scheduler...")
    scheduler.shutdown()
    logger.info("Background scheduler shutdown complete")
