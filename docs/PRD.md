# PRD - PolicyGraph AI

## 1. Product Summary

PolicyGraph AI helps healthcare operations and AI teams transform dense payer policy PDFs into structured, searchable, and validated AI-ready knowledge.

The system supports:

- healthcare policy PDF upload
- text extraction
- document chunking
- rule and entity extraction
- Graph-RAG retrieval
- policy Q&A with citations
- case validation against extracted requirements
- auditability for regulated workflows

## 2. Target Users

- Healthcare AI developers
- Claims operations analysts
- Policy review teams
- Healthcare payer/provider data teams
- GenAI implementation teams working with regulatory documents

## 3. Problem

Healthcare policy documents are long, dense, ambiguous, and difficult to convert into reliable AI workflows. A normal chatbot can retrieve similar text, but it often fails to:

- extract structured rules
- connect related policy conditions
- cite the source precisely
- validate case facts against requirements
- explain missing information
- support auditability

## 4. Goals

- Ingest healthcare policy PDFs.
- Extract text and preserve source metadata.
- Create chunks suitable for retrieval.
- Extract policy entities and rules.
- Build graph relationships from rules.
- Answer user questions with citations.
- Validate case facts against policy requirements.
- Keep the MVP runnable locally.
- Keep GCP integrations optional and configurable.

## 5. Non-Goals for MVP

- HIPAA production deployment
- Real patient data support
- Claims adjudication automation
- Full authentication/authorization
- Fine-tuned model training
- Fully managed Vertex AI Search / Matching Engine provisioning

## 6. MVP User Stories

### Upload Policy Document

As a user, I can upload a policy PDF so the system can process it.

Acceptance criteria:

- accepts PDF files
- stores file locally by default
- optionally uploads file to Google Cloud Storage
- creates a document record
- returns document ID and status

### Process Document

As a user, I can process a document so it becomes searchable and queryable.

Acceptance criteria:

- extracts text by page
- chunks text
- extracts rules
- builds graph relationships
- marks document as processed

### Ask Policy Question

As a user, I can ask a question and receive an answer based on retrieved policy evidence.

Acceptance criteria:

- uses real document retrieval
- includes citations
- includes confidence score
- returns retrieved source chunks

### Validate Case

As a user, I can enter a case and receive a policy validation result.

Acceptance criteria:

- matches procedure and case details to extracted rules
- returns likely covered, likely not covered, or needs review
- explains missing fields
- cites supporting rules

## 7. Success Metrics

- PDF ingestion works on the provided demo files.
- Query endpoint returns citations from processed documents.
- Validation endpoint identifies covered and missing-field cases.
- Frontend can complete upload -> process -> query flow.
- Code runs locally from README instructions.
