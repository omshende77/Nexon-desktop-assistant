from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from .config import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String(50), unique=True, index=True, nullable=False)
    email           = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())


class Conversation(Base):
    __tablename__ = "conversations"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True) # nullable for backwards compatibility initially, or we set a default
    title      = Column(String(255), nullable=False, default="New Chat")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Message(Base):
    __tablename__ = "messages"

    id              = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # ownership
    role            = Column(String(20), nullable=False)       # 'user' | 'assistant'
    content         = Column('content', Text, nullable=False)       # 'text' | 'images' | 'info' | 'error'
    message_type    = Column(String(20), default="text")       # 'text' | 'images' | 'info' | 'error'
    created_at      = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Task(Base):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # ownership
    title       = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    completed   = Column(Boolean, default=False, nullable=False)
    priority    = Column(String(10), default="medium")         # 'low' | 'medium' | 'high'
    due_date    = Column(String(50), nullable=True)            # ISO date string
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Note(Base):
    __tablename__ = "notes"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # ownership
    title      = Column(String(500), nullable=False)
    content    = Column(Text, nullable=False)
    tags       = Column(String(500), nullable=True)            # comma-separated tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Reminder(Base):
    __tablename__ = "reminders"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # ownership
    text        = Column(String(1000), nullable=False)
    remind_at   = Column(String(100), nullable=True)           # ISO datetime string
    completed   = Column(Boolean, default=False, nullable=False)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class Memory(Base):
    __tablename__ = "memories"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)  # ownership
    key        = Column(String(200), nullable=False, index=True)   # e.g. "name", "goal", "interest"
    value      = Column(Text, nullable=False)
    category   = Column(String(50), default="general")            # 'preference' | 'goal' | 'fact' | 'general'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
