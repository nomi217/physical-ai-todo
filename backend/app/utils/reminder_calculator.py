"""Reminder time calculator utility

Calculates the reminder_time from due_date and reminder_offset.
"""

from datetime import datetime, timedelta
from typing import Optional


# Offset mapping to timedelta
OFFSET_MAPPING = {
    "1h": timedelta(hours=1),
    "1d": timedelta(days=1),
    "3d": timedelta(days=3),
    "5d": timedelta(days=5),
    "1w": timedelta(weeks=1),
}


def calculate_reminder_time(
    due_date: Optional[datetime],
    offset: Optional[str]
) -> Optional[datetime]:
    """
    Calculate reminder_time from due_date and offset.

    Args:
        due_date: The task due date
        offset: Reminder offset string ("1h", "1d", "3d", "5d", "1w", or None)

    Returns:
        The calculated reminder time, or None if inputs are invalid

    Raises:
        ValueError: If offset is invalid or calculated time is in the past

    Examples:
        >>> due = datetime(2026, 1, 5, 15, 0)
        >>> calculate_reminder_time(due, "1d")
        datetime(2026, 1, 4, 15, 0)

        >>> calculate_reminder_time(due, None)
        None

        >>> calculate_reminder_time(None, "1d")
        None
    """
    # Return None if either input is missing
    if not due_date or not offset:
        return None

    # Get the timedelta for this offset
    delta = OFFSET_MAPPING.get(offset)
    if not delta:
        raise ValueError(
            f"Invalid offset: {offset}. Must be one of: {', '.join(OFFSET_MAPPING.keys())}"
        )

    # Calculate reminder time
    reminder_time = due_date - delta

    # Validation: reminder must be in the future
    # Make both timezone-naive for comparison
    now = datetime.utcnow()
    check_time = reminder_time.replace(tzinfo=None) if reminder_time.tzinfo else reminder_time

    if check_time <= now:
        raise ValueError(
            f"Reminder time {reminder_time} would be in the past. "
            f"Due date is too soon for offset '{offset}'"
        )

    return reminder_time
