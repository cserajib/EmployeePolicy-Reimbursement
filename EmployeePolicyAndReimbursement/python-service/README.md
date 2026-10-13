# Employee Support Desk API

A FastAPI service that answers policy-related questions for employees using approved policy records. It is designed to look up relevant policy passages, rank likely matches, and return an answer with supporting citations.

## Features

- Health check endpoint
- Policy answer endpoint for single questions
- Batch processing endpoint for multiple questions
- Date-aware and tenant/role-aware policy matching
- Prompt-injection filtering for policy text
- Citation support using matched policy chunks

## Project structure

```text
python-service/
├── app/
│   └── main.py
├── data/
│   └── policies.json
├── tests/
│   └── test_policy.py
├── requirements.txt
├── README.md
└── .pytest_cache/
```

## Requirements

- Python 3.10+
- pip

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the API

From the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

## API endpoints

### GET /health

Returns the service health status.

Example response:

```json
{
  "status": "ok"
}
```

### POST /answer

Answers a single policy question.

Request body:

```json
{
  "question": "What is my annual certification reimbursement limit?",
  "as_of": "2026-09-21",
  "tenant": "atlas",
  "role": "employee"
}
```

Example response:

```json
{
  "status": "ANSWERED",
  "answer": "The applicable annual certification reimbursement limit for atlas employees is INR 25000 as of 2026-09-21.",
  "citations": [
    {
      "chunk_id": "policy-123",
      "quote": "Employees may claim up to INR 25000 for annual certification reimbursement."
    }
  ]
}
```

### POST /batches

Processes multiple items in a single request.

Request body:

```json
{
  "batch_id": "batch-1",
  "items": [
    {
      "id": "item-1",
      "document_text": "What is my annual certification reimbursement limit?",
      "as_of": "2026-09-21",
      "tenant": "atlas",
      "role": "employee"
    }
  ]
}
```

## Policy data

The service reads policy records from `data/policies.json`.

Each record should contain approved policy data, including fields such as:

- `id`
- `tenant`
- `role`
- `approval_state`
- `effective_from`
- `effective_to`
- `passage`

This file must exist before the service can answer policy questions.

## Testing

Run the tests with:

```bash
pytest
```

## Notes

- The app uses FastAPI and Pydantic for validation.
- Input is filtered to reduce prompt-injection attempts in policy passages.
- The service is intended for internal policy lookup and should be backed with trusted policy data.
