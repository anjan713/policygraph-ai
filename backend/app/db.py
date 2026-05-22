from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .core.config import settings

engine: Engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)

SCHEMA_SQL = f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  file_name TEXT NOT NULL,
  storage_uri TEXT NOT NULL,
  status TEXT NOT NULL,
  job_id TEXT,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL,
  processed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS chunks (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  page_number INTEGER NOT NULL,
  chunk_index INTEGER NOT NULL,
  section_title TEXT,
  text TEXT NOT NULL,
  embedding vector({settings.vector_dimension}),
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS rules (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_id TEXT NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
  procedure TEXT,
  condition_text TEXT,
  requirement_text TEXT,
  decision TEXT NOT NULL,
  confidence DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS queries (
  id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  confidence DOUBLE PRECISION NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS citations (
  id TEXT PRIMARY KEY,
  query_id TEXT NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
  document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_id TEXT NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
  page_number INTEGER NOT NULL,
  excerpt TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_rules_document_id ON rules(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
"""

@contextmanager
def db_connection():
    with engine.begin() as conn:
        yield conn

def init_db() -> None:
    # SQLAlchemy execute() runs one statement at a time for psycopg.
    with engine.begin() as conn:
        for statement in [s.strip() for s in SCHEMA_SQL.split(";") if s.strip()]:
            conn.execute(text(statement))

def row_to_dict(row):
    return dict(row._mapping)
