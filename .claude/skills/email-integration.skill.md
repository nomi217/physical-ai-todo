# Email Integration Skill

## Purpose
Send professional emails with templates using Resend.

## Process

```python
import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

def send_task_email(to_email: str, task: Task):
    """Send task details via email"""
    resend.Emails.send({
        "from": "FlowTask <tasks@flowtask.dev>",
        "to": to_email,
        "subject": f"Task: {task.title}",
        "html": f"""
        <h2>{task.title}</h2>
        <p>{task.description}</p>
        <p><strong>Priority:</strong> {task.priority}</p>
        <p><strong>Tags:</strong> {', '.join(task.tags)}</p>
        """
    })

# Email-to-task: Parse incoming emails
@router.post("/api/v1/emails/incoming")
async def process_incoming_email(email_data: dict):
    # Parse email subject/body
    task = Task(
        title=email_data['subject'],
        description=email_data['body'],
        user_id=find_user_by_email(email_data['from'])
    )
    session.add(task)
    session.commit()
    return {"task_id": task.id}
```

## Output
Email sending and receiving integration.
