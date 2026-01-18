"""Reset database tables - drops and recreates all tables"""
from app.database import engine
from app.models import Task, Subtask, Note, Attachment, ActivityLog, Template, VoiceCommand, ChatMessage
from sqlmodel import SQLModel

print("Dropping all tables...")
SQLModel.metadata.drop_all(engine)
print("Creating all tables...")
SQLModel.metadata.create_all(engine)
print("Database reset complete!")
