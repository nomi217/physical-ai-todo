# Feature Specification: Task Reminders and In-App Notifications

**Feature Branch**: `006-task-reminders`
**Created**: 2025-12-30
**Status**: Draft
**Input**: User description: "Quick implementation - I'll add basic email reminders now and notifications as well"

## Clarifications

### Session 2025-12-30

- Q: How should due dates and reminder times work together? → A: Due date is primary field (with calendar + time picker). Reminder is relative offset from due date with preset options: 1 hour before, 1 day before, 3 days before, 5 days before, 1 week before, or never (no reminder).
- Q: How should the system handle overdue tasks? → A: Visual indicator (red badge/icon on overdue tasks) + send a "Task Overdue" notification to notification center when due date passes.
- Q: Where should the notification icon be placed? → A: Top navigation bar on dashboard (like standard apps - Facebook, Gmail), clicking opens dropdown panel showing notifications.
- Q: Should tasks sync to external calendars (Google Calendar, phone calendars)? → A: Simple .ics export - add "Export to Calendar" button that downloads .ics file users can import to any calendar app (Google Calendar, Apple Calendar, Outlook, etc.).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set Due Date and Reminder (Priority: P1)

Users can set a due date and time for tasks using a visual calendar picker, then choose when to be reminded (relative to the due date) from preset options. This ensures they don't miss important deadlines.

**Why this priority**: This is the core functionality - without the ability to set due dates and reminders, the entire feature has no value. This delivers immediate user value as a standalone feature.

**Independent Test**: Can be fully tested by creating a task with a due date and reminder offset, verifying both are saved correctly and the calculated reminder time is accurate. Delivers value even without notification delivery.

**Acceptance Scenarios**:

1. **Given** a user is creating a new task, **When** they select a due date of "Jan 5, 2026 3:00 PM" using the calendar picker and choose "1 day before" for reminder, **Then** the task is saved with due_date="2026-01-05 15:00" and reminder_time calculated as "2026-01-04 15:00", displaying both date badges
2. **Given** a user is editing an existing task, **When** they add a due date and select "1 week before" for reminder, **Then** the task is updated with the calculated reminder time shown in the UI
3. **Given** a user is creating a task, **When** they set a due date in the past, **Then** the system shows a validation error "Due date must be in the future"
4. **Given** a user has set a due date, **When** they select "Never" for the reminder option, **Then** the task is saved with due_date set but reminder_time is NULL (no reminder)
5. **Given** a user has set a due date very soon, **When** they try to select "1 week before" but it would be in the past, **Then** the system shows a validation error or disables that option

---

### User Story 2 - Receive In-App Notifications (Priority: P2)

Users receive in-app notifications when their task reminder time is reached or when tasks become overdue. Notifications appear in a notification center accessible from the dashboard, showing which tasks need attention.

**Why this priority**: This completes the reminder loop by actually notifying users. Depends on P1 but can be tested independently once reminder data exists.

**Independent Test**: Can be tested by creating tasks with reminder times and due dates, waiting for or simulating the trigger time, and verifying notifications appear in the notification center.

**Acceptance Scenarios**:

1. **Given** a task has a reminder time of 3:00 PM and it's now 3:00 PM, **When** the background scheduler runs, **Then** a notification is created and appears in the user's notification center
2. **Given** a task has a due date of "Jan 5, 2026 3:00 PM" and it's now past that time and the task is not completed, **When** the background scheduler runs, **Then** an "Overdue" notification is created for that task
3. **Given** a user has 3 unread notifications, **When** they open the notification center, **Then** they see a badge showing "3" and can view all pending notifications
4. **Given** a user receives a notification for "Submit report", **When** they click the notification, **Then** they are taken to that task's details
5. **Given** a notification was sent, **When** the user marks it as read, **Then** the notification is marked as read and the unread count decreases
6. **Given** a task becomes overdue, **When** the task list is displayed, **Then** that task shows a red badge or warning icon indicating it's overdue

---

### User Story 3 - View Upcoming Reminders (Priority: P3)

Users can see a list of all upcoming reminders in their dashboard to help them plan their day. This provides a quick overview of what needs attention soon.

**Why this priority**: This is a convenience feature that enhances the core reminder functionality. Can be built and tested after P1 and P2 are working.

**Independent Test**: Can be tested by creating multiple tasks with different reminder times and verifying they appear in a sorted "Upcoming Reminders" widget.

**Acceptance Scenarios**:

1. **Given** a user has 5 tasks with reminders set for today and tomorrow, **When** they view the dashboard, **Then** they see an "Upcoming Reminders" section showing the next 5 reminders in chronological order
2. **Given** a task reminder has passed, **When** the user views the dashboard, **Then** that reminder is no longer shown in the upcoming list
3. **Given** a user has no upcoming reminders, **When** they view the dashboard, **Then** the reminders widget shows "No upcoming reminders"

---

### User Story 4 - Notification Management (Priority: P4)

Users can manage their notifications by marking them as read, deleting them, or marking all as read in bulk. This keeps the notification center clean and manageable.

**Why this priority**: Quality-of-life improvement that prevents notification overload. Can be added after core notification functionality works.

**Independent Test**: Can be tested by generating multiple notifications and performing bulk actions, verifying the state changes persist.

**Acceptance Scenarios**:

1. **Given** a user has 10 unread notifications, **When** they click "Mark all as read", **Then** all notifications are marked as read and the badge count shows 0
2. **Given** a user has a notification, **When** they swipe or click delete, **Then** the notification is removed from the list
3. **Given** a user has both read and unread notifications, **When** they filter to show "Unread only", **Then** only unread notifications are displayed

---

### User Story 5 - Export Tasks to Calendar (Priority: P5)

Users can export tasks with due dates to their external calendar apps (Google Calendar, Apple Calendar, Outlook, etc.) by downloading an .ics file. This allows them to see task deadlines in their existing calendar workflow.

**Why this priority**: Nice-to-have enhancement that bridges in-app tasks with external calendar systems. Can be added independently after core features work.

**Independent Test**: Can be tested by creating tasks with due dates, clicking "Export to Calendar", downloading the .ics file, and importing it into a calendar app to verify events are created correctly.

**Acceptance Scenarios**:

1. **Given** a user has 3 tasks with due dates set, **When** they click "Export to Calendar" button in the dashboard, **Then** an .ics file is downloaded containing all tasks with due dates as calendar events
2. **Given** a user imports the downloaded .ics file into Google Calendar, **When** they view their calendar, **Then** each task appears as an event at the specified due date and time
3. **Given** a task has no due date, **When** the user exports tasks, **Then** that task is excluded from the .ics file (only tasks with due dates are exported)
4. **Given** a user exports tasks, **When** they open the .ics file in any calendar application, **Then** the task title appears as the event title and description appears in event notes

---

### Edge Cases

- What happens when a user sets a due date very close to now and selects "1 week before"?
  - System validates that the calculated reminder_time would be in the past and either shows validation error or disables/grays out that offset option
- What happens when a user sets a reminder for a task that is already completed?
  - System allows it but marks the notification as low priority or shows a warning
- What happens when multiple tasks have reminders at the same time?
  - System creates individual notifications for each task, all appear in the notification center
- What happens when the user is offline when a reminder triggers?
  - Notifications are queued and delivered when the user next accesses the app
- What happens when a user deletes a task that has a pending reminder?
  - The scheduled reminder is automatically cancelled, no notification is sent
- What happens when the background scheduler fails or crashes?
  - System implements retry logic and catches up on missed notifications when it restarts
- What happens when a user changes the due date or reminder offset after the task was created?
  - System recalculates reminder_time, cancels the old scheduled notification, and creates a new one with the updated time
- What happens when a user sets only a due date with "Never" for reminder?
  - Task shows due date badge but no reminder badge, no notification is scheduled
- What happens if a user sets a due date for 2 hours from now and selects "1 day before"?
  - System detects the offset exceeds the time until due date and shows validation error
- What happens when a user completes an overdue task?
  - The overdue visual indicator (red badge) is removed, task shows as completed, and no further overdue notifications are sent
- What happens if a user changes the due date of an overdue task to a future date?
  - The overdue status is cleared, visual indicator is removed, and the task is treated as a normal upcoming task

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to set an optional due date and time when creating a task using a visual calendar/datetime picker
- **FR-002**: System MUST allow users to set an optional due date and time when editing an existing task using a visual calendar/datetime picker
- **FR-003**: System MUST validate that due dates are set in the future (not in the past)
- **FR-003a**: System MUST provide a reminder offset dropdown with exactly these options: "1 hour before", "1 day before", "3 days before", "5 days before", "1 week before", "Never"
- **FR-003b**: System MUST automatically calculate reminder_time based on due_date minus the selected offset
- **FR-003c**: System MUST validate that the calculated reminder_time is in the future; if not, show validation error or disable invalid offset options
- **FR-004**: System MUST display visual indicators (badges/icons) on tasks showing both due date and reminder status when set
- **FR-005**: System MUST run a background scheduler that checks for tasks where reminder_time <= current_time every minute
- **FR-006**: System MUST create in-app notifications when a task's reminder time is reached
- **FR-007**: System MUST prevent duplicate notifications for the same task reminder
- **FR-008**: System MUST display a notification icon (bell icon) in the top navigation bar of the dashboard
- **FR-008a**: System MUST show the notification icon with an unread count badge when there are unread notifications
- **FR-008b**: System MUST open a dropdown panel when the notification icon is clicked, displaying all notifications (not a separate page)
- **FR-009**: System MUST display all notifications in the dropdown panel with read/unread status
- **FR-010**: System MUST allow users to mark notifications as read/unread
- **FR-011**: System MUST allow users to delete individual notifications
- **FR-012**: System MUST allow users to mark all notifications as read in bulk
- **FR-013**: System MUST link each notification to the corresponding task for quick navigation
- **FR-014**: System MUST display upcoming reminders (next 24 hours) in a dashboard widget
- **FR-015**: System MUST automatically cancel scheduled reminders when tasks are deleted
- **FR-016**: System MUST update scheduled reminders when task reminder times are changed
- **FR-017**: System MUST store notification delivery status to track sent/pending/failed notifications
- **FR-018**: System MUST show the task title and reminder time in each notification
- **FR-019**: System MUST detect when a task's due_date has passed and the task is not completed (overdue status)
- **FR-020**: System MUST create an "Overdue" notification when a task becomes overdue (due_date < current_time AND completed = false)
- **FR-021**: System MUST prevent duplicate overdue notifications for the same task (only send once when it first becomes overdue)
- **FR-022**: System MUST display a visual indicator (red badge/icon) on overdue tasks in the task list
- **FR-023**: System MUST NOT send overdue notifications for tasks that are already completed
- **FR-024**: System MUST provide an "Export to Calendar" button in the dashboard
- **FR-025**: System MUST generate an .ics (iCalendar) file containing all tasks that have due dates set
- **FR-026**: System MUST exclude tasks without due dates from the .ics export
- **FR-027**: System MUST format each task in the .ics file as a calendar event with the task title as event title and task description as event notes
- **FR-028**: System MUST set the event date/time in the .ics file to match the task's due_date
- **FR-029**: System MUST generate .ics files that are compatible with standard calendar applications (Google Calendar, Apple Calendar, Outlook, etc.)

### Key Entities

- **Notification**: Represents an in-app notification triggered by a task reminder
  - Key attributes: notification ID, task ID, user ID, title, message, read status, created timestamp, notification type
  - Relationships: belongs to a specific task and user

- **Task** (extended): Existing task entity with new due date and reminder fields
  - New attributes:
    - due_date (optional datetime) - when the task is due
    - reminder_offset (optional string enum) - user's selected offset: "1h", "1d", "3d", "5d", "1w", or NULL for "Never"
    - reminder_time (optional datetime) - calculated from due_date minus offset
    - last_notification_sent (timestamp to prevent duplicates)
  - Relationships: has many notifications

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can set a reminder time for a task in under 30 seconds using the task form
- **SC-002**: Notifications are delivered within 1 minute of the scheduled reminder time
- **SC-003**: Users can access and view their notification center in under 2 clicks from the dashboard
- **SC-004**: The notification center displays all unread notifications with accurate unread count
- **SC-005**: Users can successfully mark all notifications as read with a single action
- **SC-006**: The upcoming reminders widget displays the next 5 reminders in chronological order
- **SC-007**: System prevents duplicate notifications for the same task reminder (100% accuracy)
- **SC-008**: Background scheduler processes all pending reminders without missing any due to system load
- **SC-009**: Clicking a notification navigates to the correct task details page 100% of the time
- **SC-010**: Users can complete the full workflow (set reminder → receive notification → view task) without errors

## Assumptions

1. **No Email Service**: Email notification functionality is explicitly excluded since email service was removed from the application during signup
2. **APScheduler**: Will use APScheduler (Python) as the background task scheduler as it integrates easily with FastAPI and doesn't require separate infrastructure like Celery/Redis
3. **Notification Delivery**: In-app notifications only - users must have the app open or refresh the page to see new notifications (no push notifications to mobile devices)
4. **Timezone**: All reminder times are stored and displayed in the user's local timezone (handled by frontend)
5. **Notification Retention**: Notifications are retained indefinitely until explicitly deleted by the user
6. **Single Instance Scheduler**: The background scheduler runs as part of the existing backend service (no separate worker pods needed initially)
7. **Polling Frequency**: Background scheduler checks for due reminders every 60 seconds (1-minute granularity)
8. **Default Reminder Time**: If not specified, tasks have no reminder (reminder_time = NULL)
9. **Notification Priority**: All task reminder notifications have the same priority level
10. **Real-time Updates**: Frontend will poll for new notifications every 60 seconds or use manual refresh (no WebSocket required for MVP)

## Dependencies

- **Existing Database Schema**: The `tasks` table already has `reminder_time` field defined (Phase V schema in place)
- **Existing Authentication**: User authentication system is required to associate notifications with users
- **Existing Task CRUD**: Task creation and editing functionality must be working
- **Frontend Date/Time Picker**: Requires a datetime picker component in the React frontend
- **APScheduler Library**: Backend dependency needs to be added to requirements.txt

## Out of Scope

The following are explicitly excluded from this feature:

- **Email Notifications**: No email service integration (removed from the app)
- **SMS Notifications**: No text message notifications
- **Push Notifications**: No mobile push notifications or browser push notifications
- **Recurring Tasks**: Automatic task recurrence is not part of this feature (separate Phase V requirement)
- **Notification Sound**: No audio alerts when notifications are triggered
- **Notification Preferences**: No user settings to customize notification behavior (frequency, quiet hours, etc.)
- **Mobile Apps**: This feature targets the web application only
- **Third-party Integrations**: No Slack, Discord, or other third-party notification channels
- **Advanced Scheduling**: No "remind me X minutes before due date" logic - only preset offset options
- **Snooze Functionality**: No ability to snooze/postpone notifications
- **Real-time Calendar Sync**: No OAuth2 integration with Google Calendar/Apple Calendar for automatic two-way sync (only one-time .ics export is included)
- **Automatic Calendar Updates**: Changes to tasks after .ics export do not automatically update the calendar (user must re-export and re-import)

## Notes

- **Phase V Readiness**: The database schema already includes `reminder_time` field from Phase V planning, so no schema migration is needed for that field
- **Notification Table**: A new `notifications` table will need to be created to store notification records
- **Scheduler Persistence**: APScheduler will need to be configured to persist scheduled jobs (using database jobstore) to survive server restarts
- **Performance Consideration**: With many users, the 1-minute polling loop should be monitored for performance; can be optimized later with indexed queries
- **Future Enhancement**: This feature can be extended later with WebSocket support for real-time notifications without page refresh
