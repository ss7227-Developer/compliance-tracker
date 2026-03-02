# ComplianceHQ — Global Regulatory Compliance Dashboard

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.0-092E20?logo=django)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Celery](https://img.shields.io/badge/Celery-5.4-37814A?logo=celery)
![AWS](https://img.shields.io/badge/AWS-S3%20%7C%20SQS%20%7C%20RDS-FF9900?logo=amazon-aws)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)

A production-grade regulatory compliance tool for quality auditors to track FDA inspection trends, predict facility risk, and maintain a fully auditable data pipeline — powered by OpenFDA, AWS, and a Scikit-learn risk heuristic.

---

## Overview

ComplianceHQ ingests drug enforcement records from the [OpenFDA API](https://open.fda.gov/apis/), normalises them into a structured relational model, archives every raw record to an **AWS S3 data lake**, and exposes a filterable REST API consumed by a **React dashboard**. A Scikit-learn heuristic scores each facility's compliance risk so auditors can prioritise investigations *before* the next audit cycle.

Key engineering decisions:
- **Async-first pipeline** — data ingestion runs as a Celery task (Redis broker in dev, AWS SQS in production) so the API never blocks on long-running fetches.
- **Zero-code environment swap** — switching from local Docker to AWS RDS + SQS requires only two env-var changes; no application code changes.
- **Full auditability** — every `Inspection` row carries `created_at`, `updated_at`, a `change_log` JSONField, and a pointer back to the raw S3 object.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Docker Compose (local)                      │
│                                                                     │
│  ┌─────────────┐    HTTP     ┌─────────────────────────────────┐   │
│  │  React/Vite │ ──/api/*──▶ │     Django REST API (:8000)     │   │
│  │   (:5173)   │ ◀──JSON──── │  inspections / stats / fetch    │   │
│  └─────────────┘             └──────────────┬──────────────────┘   │
│         │                                   │ enqueue task         │
│    Vite proxy                               ▼                       │
│    /api → :8000         ┌───────────────────────────────────┐      │
│                         │     Celery Worker                  │      │
│                         │  fetch_fda_batch (max_retries=3)   │      │
│                         └──────┬────────────────┬───────────┘      │
│                                │                │                   │
│                   ┌────────────▼───┐    ┌───────▼───────┐          │
│                   │  PostgreSQL    │    │  Redis Broker  │          │
│                   │  (local) /     │    │  (local dev)   │          │
│                   │  AWS RDS (prod)│    │  AWS SQS (prod)│          │
│                   └────────────────┘    └───────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │ boto3
                    ┌─────────▼─────────┐
                    │    AWS S3          │
                    │  raw/{YYYY}/{MM}/  │
                    │  {DD}/{event}.json │
                    │  (versioned bucket)│
                    └───────────────────┘
```

**OpenFDA Classification Mapping:**

| OpenFDA Class | Internal Code | Meaning |
|---------------|--------------|---------|
| Class I | **OAI** | Official Action Indicated — immediate health hazard |
| Class II | **VAI** | Voluntary Action Indicated — moderate risk |
| Class III | **NAI** | No Action Indicated — least severe |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.12 + Django 5.0 | REST API, ORM, admin |
| | Django REST Framework 3.15 | Serializers, filtering, pagination |
| | Celery 5.4 | Async task queue (data ingestion) |
| | Scikit-learn 1.5 | Risk score heuristic |
| **Database** | PostgreSQL 16 (local) / AWS RDS (prod) | Relational store |
| **Message Broker** | Redis 7 (local) / AWS SQS (prod) | Celery transport |
| **Cloud** | AWS S3 | Immutable raw data archive |
| | AWS SQS | Production task broker |
| | AWS RDS | Production PostgreSQL |
| **Frontend** | React 18 + Vite 5 | SPA |
| | Tailwind CSS 3.4 | Utility-first styling |
| | Recharts 2.12 | Data visualisation |
| | Lucide React | Icon set |
| | Axios | HTTP client |
| **Infrastructure** | Docker Compose | Local orchestration (5 services) |
| | boto3 1.34 | AWS SDK |

---

## Features

- **Live FDA Data Ingestion** — fetches drug enforcement records from OpenFDA (`/drug/enforcement.json`) in paginated batches with automatic rate-limit handling (40 req/min)
- **AWS S3 Data Lake** — every raw API record is archived to `s3://<bucket>/raw/{YYYY}/{MM}/{DD}/{event_id}.json` with bucket versioning enabled
- **Async Celery Pipeline** — ingestion runs as a background task with 3-retry exponential backoff; triggered via management command or REST endpoint
- **AWS SQS Production Broker** — one env-var swap from Redis to SQS; no code changes required
- **AWS RDS Ready** — `DATABASE_URL` env var accepted; zero application code changes to switch from local Postgres to RDS
- **ML Risk Scoring** — Scikit-learn weighted heuristic scores each facility 0–1 based on OAI rate, inspection frequency, and recency of severe findings
- **Full Audit Schema** — every `Inspection` row has `created_at`, `updated_at`, and a `change_log` JSONField logging field-level mutations with timestamps
- **Filterable REST API** — filter by `country`, `classification`, `firm_name`, `date_from`, `date_to`; full-text search; sortable by any field
- **Interactive Dashboard** — stats grid, 12-month trend chart (Recharts), searchable/sortable compliance table with classification and risk badges
- **"Fetch Latest" Button** — React UI button triggers a Celery task asynchronously and shows the task ID for monitoring

---

## Project Structure

```
compliance_tracker/
├── .env.example                    # Config template (copy to .env)
├── docker-compose.yml              # Local dev: 5 services
├── docker-compose.prod.yml         # Production override (RDS + SQS)
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── compliance_project/
│   │   ├── settings.py             # All config via env vars
│   │   ├── celery.py               # Celery app initialisation
│   │   └── urls.py                 # Root URL conf → /api/
│   └── inspections/
│       ├── models.py               # Inspection model (audit + risk + S3 fields)
│       ├── serializers.py          # DRF serializers (list + detail)
│       ├── views.py                # ListAPIView, stats_view, trigger_fetch
│       ├── filters.py              # DjangoFilterBackend config
│       ├── tasks.py                # Celery: fetch_fda_batch (S3 + DB)
│       ├── risk.py                 # Scikit-learn risk scoring
│       ├── s3.py                   # boto3 S3 upload helper
│       ├── admin.py                # Django admin registration
│       ├── migrations/
│       │   └── 0001_initial.py
│       └── management/commands/
│           ├── wait_for_db.py      # Polls DB until ready (used in docker-compose)
│           ├── fetch_fda_data.py   # Enqueues/runs fetch_fda_batch
│           └── score_risk.py       # Runs Scikit-learn scoring, prints top-N firms
│
└── frontend/
    ├── Dockerfile
    ├── vite.config.js              # Vite proxy: /api → http://api:8000
    ├── tailwind.config.js          # Custom OAI/VAI/NAI colours
    └── src/
        ├── api/client.js           # Axios client
        ├── hooks/useInspections.js # Data fetching hook (Promise.all)
        ├── components/
        │   ├── layout/Sidebar.jsx
        │   ├── dashboard/StatsGrid.jsx
        │   ├── dashboard/TrendChart.jsx   # Recharts LineChart
        │   ├── dashboard/ComplianceTable.jsx  # Sortable + searchable
        │   └── ui/                 # LoadingSpinner, ErrorBanner
        └── pages/Dashboard.jsx
```

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- [AWS CLI](https://aws.amazon.com/cli/) + an AWS account (for S3 archival — optional for local testing)
- Git

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/compliance-tracker.git
cd compliance-tracker
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in:

```dotenv
# Required for S3 data lake archival
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=us-east-1
S3_RAW_BUCKET=compliance-tracker-raw-fda-data
```

> S3 archival is optional for local development. If `AWS_ACCESS_KEY_ID` is empty, the ingestion pipeline will skip S3 uploads and log a warning — all other functionality works normally.

**Create the S3 bucket (first time only):**
```bash
aws s3 mb s3://compliance-tracker-raw-fda-data --region us-east-1
aws s3api put-bucket-versioning \
  --bucket compliance-tracker-raw-fda-data \
  --versioning-configuration Status=Enabled
```

### 3. Start all services

```bash
docker compose up --build
```

This starts 5 containers:
| Container | Role | Port |
|-----------|------|------|
| `db` | PostgreSQL 16 | 5432 |
| `redis` | Celery broker | 6379 |
| `api` | Django REST API | **8000** |
| `celery` | Background worker | — |
| `frontend` | React dev server | **5173** |

Django runs migrations automatically on startup.

### 4. Ingest FDA data

```bash
# Fetch 300 records synchronously (no Celery worker needed)
docker compose exec api python manage.py fetch_fda_data --limit 300 --sync

# Or enqueue as a background Celery task (default)
docker compose exec api python manage.py fetch_fda_data --limit 1000

# Watch Celery worker progress
docker compose logs -f celery
```

> Without an OpenFDA API key, the rate limit is 40 requests/minute. The pipeline automatically sleeps 1.5s between batches. For higher throughput, register at [open.fda.gov](https://open.fda.gov/apis/authentication/) and add `?api_key=YOUR_KEY` to the endpoint URL.

### 5. Run risk scoring

```bash
docker compose exec api python manage.py score_risk --top 10
```

This runs the Scikit-learn heuristic against all ingested firms and updates `predicted_risk_score` on every `Inspection` row.

### 6. Open the dashboard

Navigate to **[http://localhost:5173](http://localhost:5173)**

The dashboard shows:
- **Stats grid** — total inspections, OAI%, top country
- **12-month trend chart** — Recharts line graph
- **Compliance table** — searchable, sortable, with classification badges (OAI/VAI/NAI) and risk badges (HIGH/MED/LOW)

---

## API Reference

All endpoints are prefixed with `/api/`.

### `GET /api/inspections/`

Returns a paginated list of inspection records.

| Query Param | Type | Description |
|-------------|------|-------------|
| `country` | string | Exact match (case-insensitive) |
| `classification` | `OAI` \| `VAI` \| `NAI` | Filter by classification |
| `firm_name` | string | Case-insensitive contains |
| `date_from` | `YYYY-MM-DD` | Inspections on or after this date |
| `date_to` | `YYYY-MM-DD` | Inspections on or before this date |
| `search` | string | Full-text search across firm_name, city, country |
| `ordering` | string | Sort field, prefix `-` for descending (e.g. `-predicted_risk_score`) |
| `page` | integer | Page number (50 records per page) |

**Example response:**
```json
{
  "count": 208,
  "next": "http://localhost:8000/api/inspections/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "firm_name": "McKesson",
      "inspection_date": "2026-01-16",
      "city": "Irving",
      "country": "United States",
      "classification": "OAI",
      "fda_event_id": "98366",
      "predicted_risk_score": 0.7,
      "s3_archive_key": "raw/2026/03/20/98366.json",
      "created_at": "2026-03-20T00:02:04.955929Z",
      "updated_at": "2026-03-20T00:02:04.955941Z"
    }
  ]
}
```

### `GET /api/inspections/<id>/`

Full detail view including `raw_data` (original OpenFDA JSON) and `change_log`.

### `GET /api/stats/`

Returns aggregated dashboard metrics.

```json
{
  "total_inspections": 208,
  "oai_percentage": 8.2,
  "top_countries": [
    { "country": "United States", "count": 199 },
    { "country": "India", "count": 3 }
  ],
  "monthly_trend": [
    { "month": "2025-03", "count": 1 },
    { "month": "2025-07", "count": 2 }
  ]
}
```

### `POST /api/fetch/`

Enqueues a background Celery task to fetch FDA data.

**Request body:**
```json
{ "limit": 500 }
```

**Response (HTTP 202):**
```json
{ "task_id": "a1b2c3d4-..." }
```

Monitor via `docker compose logs -f celery`.

---

## AWS Integrations

### S3 — Raw Data Archive

Every raw OpenFDA record is uploaded to S3 before being written to the database:

```
s3://<bucket>/raw/{YYYY}/{MM}/{DD}/{fda_event_id}.json
```

- Bucket versioning is enabled — overwrites are preserved, providing an immutable audit trail
- Each `Inspection` row stores `s3_archive_key` so any record can be traced back to its exact source
- Errors are logged and do not block ingestion — an S3 outage never breaks the pipeline

### SQS — Production Celery Broker

Local development uses Redis. Production switches to SQS with a single env-var change:

```dotenv
# .env (production)
CELERY_BROKER_URL=sqs://
```

Celery's SQS transport (via `celery[sqs]`) uses `boto3`, which automatically picks up `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` from the environment. No queue URL is needed — Celery auto-creates a queue named after the app.

### RDS — Production PostgreSQL

The application reads `DATABASE_URL` via `dj-database-url`. Switching from local Postgres to RDS:

```dotenv
# .env (production)
DATABASE_URL=postgres://user:pass@mydb.us-east-1.rds.amazonaws.com:5432/compliance_db
```

Zero application code changes required.

---

## Data Pipeline

```
OpenFDA API
  /drug/enforcement.json
        │
        │  paginated requests (limit=100, 1.5s sleep)
        ▼
  fetch_fda_batch (Celery @shared_task)
        │
        ├──▶ upload_batch_to_s3()
        │      boto3 → s3://<bucket>/raw/YYYY/MM/DD/{event_id}.json
        │      Logs key → s3_archive_key on Inspection row
        │
        └──▶ Inspection.objects.get_or_create(fda_event_id=...)
               Idempotent — re-running never creates duplicates
               change_log = [{"ts": "...", "event": "initial_ingest"}]
               classification = CLASS_MAP[raw_class]  # Class I→OAI etc.
```

**Classification normalisation:**

```python
CLASS_MAP = {
    "Class I":   "OAI",  # Immediate health hazard
    "Class II":  "VAI",  # Possible adverse health consequences
    "Class III": "NAI",  # Unlikely adverse consequences
}
```

---

## Risk Scoring Model

The `score_risk` management command computes a `predicted_risk_score` (0.0–1.0) per facility using a weighted linear heuristic:

| Feature | Weight | How computed |
|---------|--------|-------------|
| **OAI rate** | 50% | `oai_count / total_inspections` per firm |
| **Inspection frequency** | 30% | Total inspections, normalised to [0,1] via `MinMaxScaler` |
| **Recent OAI flag** | 20% | 1.0 if any OAI classification in the last 365 days, else 0.0 |

```python
score = 0.5 × oai_rate + 0.3 × norm_frequency + 0.2 × recent_oai_flag
```

**Why this approach:**
- OAI rate is the strongest historical predictor of future enforcement actions
- Frequency normalisation prevents large-distribution firms from dominating purely on volume
- Recency captures whether a firm is in an *active* enforcement cycle right now

**Risk bands displayed in the UI:**

| Score | Badge | Meaning |
|-------|-------|---------|
| ≥ 0.70 | 🔴 HIGH | Prioritise for immediate audit review |
| 0.40–0.69 | 🟡 MED | Monitor closely |
| < 0.40 | 🟢 LOW | Standard monitoring |

---

## Production Deployment

Use the provided Compose override file to disable local containers and point to AWS services:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

**Required environment variables for production:**

```dotenv
DJANGO_SECRET_KEY=<long-random-string>
DJANGO_DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# AWS RDS
DATABASE_URL=postgres://user:pass@mydb.us-east-1.rds.amazonaws.com:5432/compliance_db

# AWS SQS (Celery broker)
CELERY_BROKER_URL=sqs://

# AWS credentials (for S3 + SQS)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
S3_RAW_BUCKET=compliance-tracker-raw-fda-data
```

**Recommended IAM policy for the application user:**

```json
{
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:PutObject", "s3:GetObject"],
      "Resource": "arn:aws:s3:::compliance-tracker-raw-fda-data/*"
    },
    {
      "Effect": "Allow",
      "Action": ["sqs:SendMessage", "sqs:ReceiveMessage", "sqs:DeleteMessage",
                 "sqs:GetQueueAttributes", "sqs:CreateQueue"],
      "Resource": "arn:aws:sqs:us-east-1:*:compliance*"
    }
  ]
}
```

---

## Development Commands

```bash
# Start all services
docker compose up

# Run database migrations
docker compose exec api python manage.py migrate

# Create Django superuser (for /admin)
docker compose exec api python manage.py createsuperuser

# Fetch FDA data (synchronous, 300 records)
docker compose exec api python manage.py fetch_fda_data --limit 300 --sync

# Fetch FDA data (async via Celery, 1000 records)
docker compose exec api python manage.py fetch_fda_data --limit 1000

# Run risk scoring
docker compose exec api python manage.py score_risk --top 20

# Tail Celery worker logs
docker compose logs -f celery

# Django shell
docker compose exec api python manage.py shell

# Stop all services
docker compose down

# Remove all containers + volumes (full reset)
docker compose down -v
```

---

## Django Admin

Create a superuser and navigate to [http://localhost:8000/admin](http://localhost:8000/admin) to browse and search the `Inspection` table with all fields, filters, and full-text search.

```bash
docker compose exec api python manage.py createsuperuser
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with [OpenFDA](https://open.fda.gov/) · Deployed with AWS · Visualised with Recharts*
