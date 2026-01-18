"""Validation logic for Task data model.

This module provides validation functions for task title, description,
and complete task data.
"""

from typing import Optional, List


def validate_title(title: str) -> Optional[str]:
    """
    Validate task title.

    Args:
        title: The title string to validate

    Returns:
        None if valid, error message string if invalid

    Rules:
        - Required (not None or empty)
        - After strip(), must have at least 1 character
        - Maximum 200 characters
    """
    if not title:
        return "Title is required"

    if not title.strip():
        return "Title cannot be only whitespace"

    if len(title) > 200:
        return f"Title must be 200 characters or less (current: {len(title)} characters)"

    return None


def validate_description(description: str) -> Optional[str]:
    """
    Validate task description.

    Args:
        description: The description string to validate

    Returns:
        None if valid, error message string if invalid

    Rules:
        - Optional (can be empty)
        - Maximum 2000 characters
    """
    if description and len(description) > 2000:
        return f"Description must be 2000 characters or less (current: {len(description)} characters)"

    return None


def validate_task_data(title: str, description: str = "") -> List[str]:
    """
    Validate complete task data.

    Args:
        title: Task title
        description: Task description (optional)

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    title_error = validate_title(title)
    if title_error:
        errors.append(title_error)

    desc_error = validate_description(description)
    if desc_error:
        errors.append(desc_error)

    return errors
