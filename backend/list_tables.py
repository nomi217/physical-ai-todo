from sqlmodel import create_engine, Session, text
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with Session(engine) as session:
    result = session.execute(text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema='public' ORDER BY table_name"
    ))

    print("\n=== Tables in database ===")
    tables = [row[0] for row in result]
    for table in tables:
        print(f"  - {table}")
    print(f"\nTotal: {len(tables)} tables")
