"""
model_versioning.py

This snippet uses MLflow to track model training runs, logging metrics, parameters, and model artifacts.
When stakeholders question model changes or regulators demand evidence of compliance, these logs provide an audit trail.

Key concepts:
- MLflow for experiment tracking
- Storing accuracy and model artifacts for each run
- Facilitating reproducibility and regulatory audits
"""

import mlflow
import mlflow.sklearn

def track_experiment(run_name: str, pipeline, X_train, y_train, X_val, y_val):
    """
    Train the model using a given pipeline, log metrics and model artifacts to MLflow.

    Args:
        run_name (str): A name for the MLflow run (e.g., "experiment_2024_11_01")
        pipeline: The sklearn pipeline or estimator to fit.
        X_train, y_train: Training data
        X_val, y_val: Validation data

    Returns:
        The trained pipeline after logging to MLflow.
    """
    with mlflow.start_run(run_name=run_name):
        pipeline.fit(X_train, y_train)
        accuracy = pipeline.score(X_val, y_val)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.sklearn.log_model(pipeline, "model")
        print(f"MLflow run '{run_name}' logged with accuracy: {accuracy:.4f}")
    return pipeline
