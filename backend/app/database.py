import os
from typing import Optional
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./data/ai_agent_builder.db')

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)
    _ensure_agent_column(
        'api_key',
        'ALTER TABLE agents ADD COLUMN api_key VARCHAR'
    )
    _ensure_agent_column(
        'provider',
        "ALTER TABLE agents ADD COLUMN provider VARCHAR DEFAULT 'openai'",
        "UPDATE agents SET provider='openai' WHERE provider IS NULL"
    )

def _ensure_agent_column(column_name: str, alter_sql: str, post_sql: Optional[str] = None):
    inspector = inspect(engine)
    columns = {col['name'] for col in inspector.get_columns('agents')}
    if column_name in columns:
        return
    with engine.begin() as conn:
        conn.execute(text(alter_sql))
        if post_sql:
            conn.execute(text(post_sql))
