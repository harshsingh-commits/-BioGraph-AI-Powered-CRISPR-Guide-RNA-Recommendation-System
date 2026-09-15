import json
import os
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4


def track_experiment(state):
    ranked = state.get("ranked_guides", [])
    top = ranked[0] if ranked else {}
    record = {
        "experiment_id": str(uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "gene": state.get("gene_name", "N/A"),
        "guide": top.get("guide", "N/A"),
        "efficiency": top.get("efficiency", 0),
        "risk": top.get("risk", "UNKNOWN"),
        "risk_score": top.get("risk_score", 100),
        "final_score": top.get("final_score", 0),
        "model_version": os.getenv(
            "BIOGRAPH_MODEL_VERSION", state.get("scoring_model", "gc_heuristic")
        ),
        "off_target_mode": state.get("off_target_mode", "local_estimate"),
    }
    backend = os.getenv("BIOGRAPH_TRACKING_BACKEND", "jsonl").lower()
    tracking_dir = Path(__file__).resolve().parents[1] / "reports"
    tracking_dir.mkdir(parents=True, exist_ok=True)
    tracking_path = tracking_dir / "experiments.jsonl"

    if backend == "mlflow":
        try:
            import mlflow

            mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "file:./reports/mlruns"))
            with mlflow.start_run(run_name=record["gene"]):
                mlflow.log_params(
                    {
                        "gene": record["gene"],
                        "guide": record["guide"],
                        "model_version": record["model_version"],
                    }
                )
                mlflow.log_metrics(
                    {
                        "efficiency": record["efficiency"],
                        "risk_score": record["risk_score"],
                        "final_score": record["final_score"],
                    }
                )
            return {
                "experiment_id": record["experiment_id"],
                "tracking_backend": "mlflow",
                "tracking_path": os.getenv("MLFLOW_TRACKING_URI", "file:./reports/mlruns"),
            }
        except ImportError:
            backend = "jsonl"

    if backend == "wandb":
        try:
            import wandb

            run = wandb.init(
                project=os.getenv("WANDB_PROJECT", "biograph"),
                config=record,
                reinit="finish_previous",
            )
            run.log(
                {
                    "efficiency": record["efficiency"],
                    "risk_score": record["risk_score"],
                    "final_score": record["final_score"],
                }
            )
            run.finish()
            return {
                "experiment_id": record["experiment_id"],
                "tracking_backend": "wandb",
                "tracking_path": "wandb",
            }
        except ImportError:
            backend = "jsonl"

    with tracking_path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")
    return {
        "experiment_id": record["experiment_id"],
        "tracking_backend": "jsonl",
        "tracking_path": str(tracking_path),
    }
