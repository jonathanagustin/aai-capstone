"""
hyperparameter_optimization.py

This script demonstrates hyperparameter optimization using Bayesian search.
By logging trials and results, we maintain a transparent, reproducible optimization process.
This approach helps us find better performing models while preserving fairness and compliance considerations.

Key concepts:
- BayesSearchCV for efficient hyperparameter tuning
- Data-driven approach to model improvement
- Ensuring reproducibility by logging configurations
"""

from skopt import BayesSearchCV
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def optimize_hyperparameters(X_train, y_train):
    """
    Use Bayesian optimization to find the best hyperparameters for a logistic regression model.

    Args:
        X_train: Training features.
        y_train: Training labels.

    Returns:
        A BayesSearchCV object trained on the dataset.
    """
    pl = Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression(max_iter=1000))])
    param_space = {'clf__C': (1e-3, 1e3, 'log-uniform')}
    opt = BayesSearchCV(pl, param_space, n_iter=20, scoring='f1', cv=3)
    opt.fit(X_train, y_train)
    print("Hyperparameter optimization complete. Best params:", opt.best_params_)
    return opt
