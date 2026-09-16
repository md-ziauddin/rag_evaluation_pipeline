"""
MLflow Experiment Tracker.

Manages experiment creation, parameter logging, metric tracking, and artifact logging.
"""

from typing import Any

import mlflow
from mlflow.tracking import MlflowClient

from rag_eval.config.settings import settings


class MLflowTracker:
    """
    MLflow tracking helper for logging pipeline benchmarks and physician feedback.
    """

    def __init__(
        self,
        experiment_name: str = "medical_rag_evaluation",
        tracking_uri: str | None = None,
    ):
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri or settings.MLFLOW_TRACKING_URI
        try:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)
        except Exception as e:
            # Fallback gracefully if tracking server is offline
            import logging

            logging.getLogger(__name__).debug("MLflow tracking server unavailable: %s", e)

    @property
    def client(self) -> MlflowClient:
        """Returns the MLflow tracking client."""
        return MlflowClient(tracking_uri=self.tracking_uri)

    def start_run(self, run_name: str | None = None, tags: dict[str, str] | None = None) -> Any:
        """Start an MLflow active run context manager."""
        return mlflow.start_run(run_name=run_name, tags=tags)

    def log_params(self, params: dict[str, Any]) -> None:
        """Log parameter dictionary to current MLflow run."""
        mlflow.log_params(params)

    def log_metrics(self, metrics: dict[str, float]) -> None:
        """Log metric dictionary to current MLflow run."""
        mlflow.log_metrics(metrics)

    def log_feedback(self, run_id: str, rating: int, comments: str | None = None) -> None:
        """Log physician feedback (1-5 star rating) to a specific run."""
        self.client.log_metric(run_id, "physician_rating", float(rating))
        if comments:
            self.client.log_param(run_id, "physician_comments", comments)

    def log_evaluation_run(
        self,
        run_name: str,
        params: dict[str, Any],
        metrics: dict[str, float],
        artifacts: list[str] | None = None,
    ) -> str:
        """
        Log an evaluation run to MLflow server.

        Args:
            run_name: Human-readable run name (e.g. 'qdrant_bge_hybrid_linear').
            params: Dictionary of configuration parameters.
            metrics: Dictionary of numerical evaluation scores.
            artifacts: Optional list of file paths to attach to MLflow run.

        Returns:
            MLflow run ID string.
        """
        with self.start_run(run_name=run_name) as run:
            # 1. Log configuration parameters
            self.log_params(params)

            # 2. Log numerical metrics
            self.log_metrics(metrics)

            # 3. Log artifacts (reports/plots)
            if artifacts:
                for file_path in artifacts:
                    mlflow.log_artifact(file_path)

            return str(run.info.run_id)
