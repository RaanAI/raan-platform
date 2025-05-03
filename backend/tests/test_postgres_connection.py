from sqlalchemy import create_engine, text
import os

def test_postgres_connection():
    db_url = os.getenv("DATABASE_URL", "postgresql://raan:securepass@localhost:5432/raan_db")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector';"))
        extension = result.fetchone()
        assert extension is not None, "pgvector extension is not enabled"
