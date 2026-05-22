# Security and Compliance Notes

This project is for portfolio and technical demonstration use. It is not production-ready for real PHI.

## Do Not Use Real PHI in MVP

Use only synthetic demo documents.

## Production Requirements

Before using real healthcare data:

- HIPAA review
- BAAs with cloud vendors
- encryption at rest
- encryption in transit
- tenant isolation
- access control
- audit logging
- data retention controls
- PHI redaction strategy
- model/provider data policy review

## Security Controls in MVP

- `.env` ignored
- local uploads ignored
- no credentials committed
- GCP profile selected through environment variables
- local-first mode avoids accidental cloud charges

## GCP IAM Guidance

Use least privilege policies for:

- Google Cloud Storage bucket access
- PaddleOCR operations
- Vertex AI / Gemini invocation
- CloudWatch logging

Avoid administrator access for application runtime roles.
