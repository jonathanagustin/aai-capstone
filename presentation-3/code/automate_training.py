"""
automate_training.py

This script illustrates automating the model training process using scikit-learn's Pipeline.
By chaining preprocessing (e.g., scaling) and a classifier (e.g., LogisticRegression),
we ensure consistent, reproducible training steps.

Key concepts:
- Pipelines for reproducible training
- Ensuring each code commit triggers training via CI/CD
- Laying groundwork for further automation (hyperparameter tuning, fairness checks)
"""

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

def create_and_train_pipeline(X_train, y_train):
    """
    Create a training pipeline that scales numeric features and
    fits a logistic regression classifier.

    Args:
        X_train: Training feature matrix.
        y_train: Training labels.

    Returns:
        A trained sklearn Pipeline object.
    """
    pl = Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression(max_iter=1000))])
    pl.fit(X_train, y_train)
    print("Training pipeline completed successfully.")
    return pl
