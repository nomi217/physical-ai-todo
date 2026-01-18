from sqlmodel import create_engine, Session, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with Session(engine) as session:
    # Get all tasks with their user info
    result = session.execute(text(
        """
        SELECT t.id, t.title, t.user_id, u.email
        FROM task t
        LEFT JOIN "user" u ON t.user_id = u.id
        ORDER BY t.id
        """
    ))

    print("\n=== All Tasks ===")
    print(f"{'ID':<5} {'Title':<30} {'User ID':<10} {'Email':<30}")
    print("-" * 80)

    for row in result:
        task_id, title, user_id, email = row
        print(f"{task_id:<5} {title[:30]:<30} {user_id:<10} {email or 'N/A':<30}")

    # Get user count
    result = session.execute(text("SELECT COUNT(*) FROM \"user\""))
    user_count = result.scalar()
    print(f"\nTotal users: {user_count}")

    # Get task count
    result = session.execute(text("SELECT COUNT(*) FROM task"))
    task_count = result.scalar()
    print(f"Total tasks: {task_count}")
