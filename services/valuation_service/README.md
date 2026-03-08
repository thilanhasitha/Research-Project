# Valuation Engine (FastAPI)

This service pulls company data from the CSE public APIs and stores it in Postgres.

## Setup

1) Copy `.env.example` to `.env` and set values as needed.

2) Start Postgres via Docker Compose (from this folder):

```bash
docker compose up -d
```

3) Install dependencies and create tables:

```bash
pip install -r requirements.txt
python -m app.db.init_db
```

4) Run the API:

```bash
uvicorn app.main:app --reload --app-dir .
```

API base path: `/api/v1`

## Endpoints

- `GET /api/v1/health` – healthcheck.
- `POST /api/v1/cse/sync-basic` – stores the list of securities (symbol, name).
- `POST /api/v1/cse/sync-details` – fetches and stores full details for all securities (slow).
- `POST /api/v1/cse/sync-symbol?symbol=SYMB.N0000` – fetches and stores details for a single symbol.
- `GET /api/v1/cse/securities` – returns cached securities with annual/quarterly reports.

## Notes

- CDN base for logos: `https://cdn.cse.lk/cmt/`.
- CDN base for reports: `https://cdn.cse.lk/`.
- The service stores report metadata and the CDN-relative `path`. The API response includes `url` computed as `{CDN_REPORT_BASE}{path}`.
