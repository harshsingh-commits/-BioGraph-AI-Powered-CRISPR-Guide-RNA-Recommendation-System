import os
import tempfile
import time
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

from backend.auth import authenticate, require_roles
from graph import graph
from utils.evaluation import compare_guides, evaluate_guides

app = FastAPI(title="BioGraph API", version="1.0.0")
ANALYSIS_COUNT = Counter("biograph_analysis_total", "Completed analyses")
GUIDE_COUNT = Counter("biograph_guides_generated_total", "Generated guides")
ERROR_COUNT = Counter("biograph_errors_total", "API errors")
ANALYSIS_RUNTIME = Histogram("biograph_analysis_runtime_seconds", "Analysis runtime")


class EvaluationRequest(BaseModel):
    predictions: list[dict] = Field(default_factory=list)
    labels: list[dict] = Field(default_factory=list)


class ComparisonRequest(BaseModel):
    guide_a: dict
    guide_b: dict


class LoginRequest(BaseModel):
    username: str
    password: str


def public_state(result):
    return {key: value for key, value in result.items() if key != "sequence"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "biograph-api"}


@app.post("/auth/login")
def login(request: LoginRequest):
    return authenticate(request.username, request.password)


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...), _user=Depends(require_roles("Researcher", "Admin"))
):
    started = time.perf_counter()
    suffix = Path(file.filename or "sequence.fasta").suffix or ".fasta"
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(contents)
        temp_path = temp_file.name
    try:
        chromosomes = [
            item.strip()
            for item in os.getenv("BIOGRAPH_CHROMOSOMES", "").split(",")
            if item.strip()
        ]
        result = graph.invoke({"fasta_file": temp_path, "chromosomes": chromosomes})
        persistence = "disabled"
        if os.getenv("DATABASE_URL"):
            try:
                from database.store import persist_result

                persist_result(result)
                persistence = "postgresql"
            except Exception:
                persistence = "unavailable"
        response = public_state(result)
        response["persistence"] = persistence
        ANALYSIS_COUNT.inc()
        GUIDE_COUNT.inc(len(result.get("candidate_guides", [])))
        return response
    except Exception as error:
        ERROR_COUNT.inc()
        raise HTTPException(status_code=422, detail=str(error)) from error
    finally:
        ANALYSIS_RUNTIME.observe(time.perf_counter() - started)
        Path(temp_path).unlink(missing_ok=True)


@app.post("/evaluate")
def evaluate(request: EvaluationRequest, _user=Depends(require_roles("Reviewer", "Admin"))):
    return evaluate_guides(request.predictions, request.labels)


@app.post("/compare")
def compare(request: ComparisonRequest, _user=Depends(require_roles("Reviewer", "Admin"))):
    return compare_guides(request.guide_a, request.guide_b)
