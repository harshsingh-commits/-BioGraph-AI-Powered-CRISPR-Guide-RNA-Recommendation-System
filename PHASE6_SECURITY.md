# BioGraph Phase 6: Security, CI, and Monitoring

## JWT roles

Set a non-default secret before running the API:

```powershell
$env:BIOGRAPH_JWT_SECRET = "replace-with-a-long-random-secret"
py -m uvicorn backend.main:app --port 8000
```

Development users are available only while `BIOGRAPH_ALLOW_DEV_USERS=true`:

- `researcher / researcher`: analyze sequences
- `reviewer / reviewer`: evaluate and compare guides
- `admin / admin`: all protected operations

For deployment, set `BIOGRAPH_USERS` to a JSON object and disable development users.

## CI

GitHub Actions runs pytest, Ruff, Black, Python compilation, and Docker build on pushes and pull requests. The workflow is in `.github/workflows/ci.yml`.

## Monitoring

FastAPI exposes `/metrics` with analysis count, runtime histogram, error count, and generated-guide count. Compose provisions Prometheus and Grafana:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (`admin` / `admin` in development)