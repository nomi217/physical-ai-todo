from sqlmodel import create_engine, Session, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with Session(engine) as session:
    result = session.execute(text(
        "SELECT EXISTS (SELECT FROM information_schema.tables "
        "WHERE table_schema='public' AND table_name='conversation_messages')"
    ))
    exists = result.scalar()
    print('conversation_messages table exists:', exists)

    if exists:
        # Get column names
        result = session.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='conversation_messages' ORDER BY ordinal_position"
        ))
        columns = [row[0] for row in result]
        print('Columns:', ', '.join(columns))
