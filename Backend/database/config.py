import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Failsafe flag - if false, application should fall back to localStorage/memory
DB_AVAILABLE = False
engine = None
SessionLocal = None

try:
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL)
        # Eagerly test the connection
        with engine.connect() as conn:
            pass
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DB_AVAILABLE = True
        print("[Database] Successfully configured PostgreSQL connection.")
    else:
        print("[Database] Warning: DATABASE_URL not found in .env. Running in ephemeral mode.")
except Exception as e:
    print(f"[Database] Error configuring database: {e}. Running in ephemeral mode.")
    DB_AVAILABLE = False
    engine = None
    SessionLocal = None

Base = declarative_base()

def get_db():
    if not DB_AVAILABLE:
        yield None
        return
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
