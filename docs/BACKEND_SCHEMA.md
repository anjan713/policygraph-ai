# Backend Schema

The local MVP uses SQLite. Production can migrate to PostgreSQL with equivalent table definitions.

## documents

Stores uploaded policy documents.

```sql
CREATE TABLE documents (
  id TEXT PRIMARY KEY,
  file_name TEXT NOT NULL,
  storage_uri TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TEXT NOT NULL,
  processed_at TEXT
);
```

## chunks

Stores extracted document chunks.

```sql
CREATE TABLE chunks (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL,
  page_number INTEGER NOT NULL,
  chunk_index INTEGER NOT NULL,
  section_title TEXT,
  text TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(document_id) REFERENCES documents(id)
);
```

## rules

Stores extracted healthcare policy rules.

```sql
CREATE TABLE rules (
  id TEXT PRIMARY KEY,
  document_id TEXT NOT NULL,
  chunk_id TEXT NOT NULL,
  procedure TEXT,
  condition_text TEXT,
  requirement_text TEXT,
  decision TEXT NOT NULL,
  confidence REAL NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(document_id) REFERENCES documents(id),
  FOREIGN KEY(chunk_id) REFERENCES chunks(id)
);
```

## graph_nodes

```sql
CREATE TABLE graph_nodes (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  type TEXT NOT NULL,
  properties_json TEXT NOT NULL
);
```

## graph_edges

```sql
CREATE TABLE graph_edges (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  target_id TEXT NOT NULL,
  relationship TEXT NOT NULL,
  properties_json TEXT NOT NULL
);
```

## queries

```sql
CREATE TABLE queries (
  id TEXT PRIMARY KEY,
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  confidence REAL NOT NULL,
  created_at TEXT NOT NULL
);
```

## citations

```sql
CREATE TABLE citations (
  id TEXT PRIMARY KEY,
  query_id TEXT NOT NULL,
  document_id TEXT NOT NULL,
  chunk_id TEXT NOT NULL,
  page_number INTEGER NOT NULL,
  excerpt TEXT NOT NULL,
  FOREIGN KEY(query_id) REFERENCES queries(id)
);
```
