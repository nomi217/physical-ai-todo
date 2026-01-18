"""
Notification API routes for in-app notifications.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app import crud
from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models import User
from app.schemas import NotificationRead

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def get_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    type: Optional[str] = Query(None, description="Filter by type (reminder/overdue)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get user's notifications with optional filtering.

    **Query Parameters:**
    - **is_read**: Filter by read status (true/false)
    - **type**: Filter by notification type (reminder/overdue)
    - **limit**: Max notifications per page (1-100, default: 50)
    - **offset**: Number to skip (default: 0)

    **Returns:**
    - List of notifications sorted by created_at descending (newest first)
    """
    notifications = crud.get_notifications(
        session=session,
        user_id=current_user.id,
        is_read=is_read,
        type=type,
        limit=limit,
        offset=offset
    )

    return [NotificationRead.model_validate(n) for n in notifications]


@router.get("/unread-count", response_model=dict)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get count of unread notifications for the current user.

    **Returns:**
    ```json
    {
      "unread_count": 5
    }
    ```
    """
    count = crud.get_unread_count(session=session, user_id=current_user.id)

    return {"unread_count": count}


@router.patch("/{notification_id}", response_model=NotificationRead)
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Mark a notification as read.

    **Path Parameters:**
    - **notification_id**: Notification ID to mark as read

    **Returns:**
    - Updated notification object

    **Raises:**
    - 404: Notification not found or access denied
    """
    notification = crud.mark_notification_as_read(
        session=session,
        notification_id=notification_id,
        user_id=current_user.id
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail=f"Notification {notification_id} not found or access denied"
        )

    return NotificationRead.model_validate(notification)


@router.post("/mark-all-read", response_model=dict)
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Mark all user's notifications as read.

    **Returns:**
    ```json
    {
      "success": true,
      "updated_count": 12,
      "message": "Marked 12 notifications as read"
    }
    ```
    """
    count = crud.mark_all_notifications_as_read(
        session=session,
        user_id=current_user.id
    )

    return {
        "success": True,
        "updated_count": count,
        "message": f"Marked {count} notification(s) as read"
    }


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a notification.

    **Path Parameters:**
    - **notification_id**: Notification ID to delete

    **Returns:**
    - No content (204)

    **Raises:**
    - 404: Notification not found or access denied
    """
    deleted = crud.delete_notification(
        session=session,
        notification_id=notification_id,
        user_id=current_user.id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Notification {notification_id} not found or access denied"
        )

    return None


@router.delete("/read", status_code=200)
def delete_read_notifications(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete all read notifications for the current user.

    **Returns:**
    ```json
    {
      "success": true,
      "deleted_count": 8,
      "message": "Deleted 8 read notifications"
    }
    ```
    """
    count = crud.delete_read_notifications(
        session=session,
        user_id=current_user.id
    )

    return {
        "success": True,
        "deleted_count": count,
        "message": f"Deleted {count} read notification(s)"
    }
