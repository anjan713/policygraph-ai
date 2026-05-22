# Graph Schema

The MVP stores graph data in SQLite tables. The schema is compatible with a future Neo4j migration.

## Node Types

### Document

Represents a policy PDF.

Properties:

- `document_id`
- `file_name`

### Chunk

Represents a source text chunk.

Properties:

- `chunk_id`
- `document_id`
- `page_number`

### Procedure

Represents a healthcare procedure.

Examples:

- MRI lumbar spine
- Prior authorization
- HbA1c testing

### Requirement

Represents a required condition.

Examples:

- 6 weeks conservative treatment
- symptoms persist
- prior authorization required

### Decision

Represents a policy decision.

Examples:

- covered
- not covered
- requires review

## Relationships

```text
Document HAS_CHUNK Chunk
Chunk MENTIONS_PROCEDURE Procedure
Procedure REQUIRES Requirement
Procedure HAS_DECISION Decision
Requirement SUPPORTED_BY Chunk
Decision SUPPORTED_BY Chunk
```

## Example

```text
MRI_Coverage_Policy.pdf
  HAS_CHUNK -> page 1 chunk 0
page 1 chunk 0
  MENTIONS_PROCEDURE -> MRI lumbar spine
MRI lumbar spine
  REQUIRES -> 6 weeks conservative treatment
MRI lumbar spine
  HAS_DECISION -> covered
6 weeks conservative treatment
  SUPPORTED_BY -> page 1 chunk 0
```
