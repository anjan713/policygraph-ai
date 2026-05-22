# Demo Guide

## Start the full stack

```bash
cp .env.example .env
docker compose up --build
```

## Upload and process

1. Go to `http://localhost:3000/upload`.
2. Upload `demo_files/MRI_Coverage_Policy.pdf`.
3. Click **Process in Background**.
4. Wait for the status badge to change from `queued` to `processing` to `processed`.

## Ask a question

Go to `http://localhost:3000/query` and ask:

```text
Is MRI lumbar spine covered after 6 weeks of conservative treatment?
```

Expected behavior:

- The answer includes a coverage-style decision.
- Citations include chunk/page evidence.
- Graph context appears if Neo4j was available during processing.

## Validate a case

Go to `http://localhost:3000/validate` and submit:

```json
{
  "procedure": "MRI lumbar spine",
  "diagnosis": "lower back pain",
  "conservative_treatment_weeks": 6,
  "symptoms_persist": true
}
```
