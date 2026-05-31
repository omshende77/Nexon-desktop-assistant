import sys
sys.path.insert(0, '.')

from Backend.database.config import DB_AVAILABLE, engine, SessionLocal
print(f'DB_AVAILABLE: {DB_AVAILABLE}')

if not DB_AVAILABLE:
    print('DB not available! Check your DATABASE_URL and PostgreSQL password.')
    sys.exit(1)

from Backend.database.models import Conversation, Message
from sqlalchemy import inspect, text

# Check tables exist
insp = inspect(engine)
tables = insp.get_table_names()
print(f'Tables in DB: {tables}')

db = SessionLocal()
try:
    # Check conversations
    convos = db.query(Conversation).all()
    print(f'\nConversations in DB: {len(convos)}')
    for c in convos[:10]:
        msgs = db.query(Message).filter(Message.conversation_id == c.id).count()
        print(f'  - ID={c.id} | title="{c.title}" | messages={msgs} | updated={c.updated_at}')

    # Check total messages
    total_msgs = db.query(Message).count()
    print(f'\nTotal messages in DB: {total_msgs}')

    # Sample messages
    sample_msgs = db.query(Message).order_by(Message.created_at.desc()).limit(5).all()
    print('\nLatest 5 messages:')
    for m in sample_msgs:
        print(f'  - conv={m.conversation_id} | role={m.role} | content="{m.content[:60]}..."')

    # Check DB URL (redacted)
    from dotenv import dotenv_values
    env = dotenv_values('.env')
    url = env.get('DATABASE_URL', 'NOT SET')
    print(f'\nDATABASE_URL: {url}')

except Exception as e:
    print(f'Error querying DB: {e}')
finally:
    db.close()

print('\nDiagnostic complete.')
