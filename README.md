# Payment Reconciliation System

An automated financial reconciliation engine built with **Python & FastAPI** to match internal business transactions against payment gateway settlement reports (e.g. Midtrans, Xendit, DOKU).

It detects financial discrepancies, missing settlements, duplicate records, status mismatches, and generates structured audit summaries.

---

## Features

- Multi-source CSV ingestion: internal transactions + payment gateway settlement reports
- Discrepancy detection:
  - `MATCHED`
  - `AMOUNT_MISMATCH`
  - `STATUS_MISMATCH`
  - `MISSING_IN_GATEWAY`
  - `MISSING_IN_INTERNAL`
  - `DUPLICATE_IN_GATEWAY`
- JSON API report output
- CSV audit report export
- Docker-ready deployment
- Pytest test suite

---

## Tech Stack

- Python 3.12+
- FastAPI
- Pydantic v2
- Pytest
- Docker / Docker Compose

---

## Project Structure

```text
payment-reconciliation-system/
├── app/
│   ├── config.py
│   ├── csv_parser.py
│   ├── main.py
│   ├── models.py
│   ├── reconciliation.py
│   └── reporting.py
├── samples/
│   ├── internal_transactions.csv
│   └── gateway_settlement.csv
├── tests/
│   └── test_reconciliation.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Quick Start

```bash
git clone https://github.com/budsantoso/payment-reconciliation-system.git
cd payment-reconciliation-system

uv venv .venv
. .venv/Scripts/activate  # Windows Git Bash
uv pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open:

```text
http://localhost:8000/docs
http://localhost:8000/health
```

---

## API Usage

### JSON reconciliation report

```bash
curl -X POST http://localhost:8000/reconcile \
  -F "internal_file=@samples/internal_transactions.csv" \
  -F "gateway_file=@samples/gateway_settlement.csv"
```

### CSV audit export

```bash
curl -X POST http://localhost:8000/reconcile.csv \
  -F "internal_file=@samples/internal_transactions.csv" \
  -F "gateway_file=@samples/gateway_settlement.csv" \
  --output reconciliation_audit.csv
```

---

## Example Result

```json
{
  "summary": {
    "total_internal_records": 5,
    "total_gateway_records": 6,
    "matched_count": 1,
    "discrepancy_count": 5,
    "total_internal_amount": "575000",
    "total_gateway_amount": "485000",
    "amount_difference": "90000",
    "breakdown": {
      "AMOUNT_MISMATCH": 1,
      "DUPLICATE_IN_GATEWAY": 1,
      "MATCHED": 1,
      "MISSING_IN_GATEWAY": 1,
      "MISSING_IN_INTERNAL": 1,
      "STATUS_MISMATCH": 1
    }
  }
}
```

---

## Run Tests

```bash
pytest
```

---

## Docker

```bash
cp .env.example .env
docker compose up --build
```

---

## Production Notes

This demo keeps storage stateless and file-based. For production, add:

- PostgreSQL report persistence
- background jobs for large settlement files
- gateway-specific adapters for Midtrans, Xendit, DOKU
- audit logs and approval workflow
- role-based access control
- scheduled reconciliation jobs
