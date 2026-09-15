# BioGraph Phase 5: Reproducibility and Deployment

## Local API

```powershell
py -m uvicorn backend.main:app --reload --port 8000
```

Endpoints:

- `GET /health`
- `POST /analyze` with a FASTA file
- `POST /evaluate` with prediction and label JSON
- `POST /compare` with two guide records

## Docker Compose

```powershell
docker compose up --build
```

- Streamlit: `http://localhost:8501`
- FastAPI docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

The database schema contains `genes`, `guides`, `off_targets`, `experiments`, and `reports`. The API persists completed experiments when `DATABASE_URL` is configured; local runs continue with JSONL tracking when Postgres is absent.

When `BIOGRAPH_API_URL` is set, Streamlit uploads sequences to FastAPI instead of invoking LangGraph in-process. The Docker Compose frontend sets this automatically; local Streamlit runs use the direct graph fallback.

## Experiment tracking

Default tracking writes `reports/experiments.jsonl`. Optional backends:

```powershell
$env:BIOGRAPH_TRACKING_BACKEND = "mlflow"
$env:MLFLOW_TRACKING_URI = "file:./reports/mlruns"
```

or:

```powershell
$env:BIOGRAPH_TRACKING_BACKEND = "wandb"
$env:WANDB_PROJECT = "biograph"
```

Install the selected optional package separately because MLflow and W&B are large integrations.