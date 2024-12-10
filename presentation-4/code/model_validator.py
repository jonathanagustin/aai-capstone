"""
model_validator.py

This script acts as a quality gate in the CI/CD pipeline:
- Checks performance metrics (accuracy, F1, AUC)
- Ensures fairness (disparity ratio)
- Confirms latency meets p95 threshold

If any check fails, it prints an error and exits non-zero to block deployment.
"""

import sys
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

class ModelValidator:
    def __init__(self, performance_thresholds, fairness_thresholds, latency_threshold):
        """
        Args:
            performance_thresholds (dict): e.g. {'accuracy':0.9, 'f1':0.8}
            fairness_thresholds (dict): e.g. {'max_disparity':0.8}
            latency_threshold (float): p95 latency max allowed (e.g. 0.5s)
        """
        self.performance_thresholds = performance_thresholds
        self.fairness_thresholds = fairness_thresholds
        self.latency_threshold = latency_threshold
        self.validation_results = {}

    def validate_performance(self, y_true, y_pred, y_prob):
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'roc_auc': roc_auc_score(y_true, y_prob),
            'f1': f1_score(y_true, y_pred)
        }
        self.validation_results['performance'] = metrics
        return all(metrics[m]>=self.performance_thresholds[m] for m in self.performance_thresholds)

    def validate_fairness(self, subgroup_scores):
        # subgroup_scores: {'priv':score, 'unpriv':score}
        disparity = subgroup_scores['unpriv'] / subgroup_scores['priv']
        self.validation_results['fairness'] = {'disparity':disparity}
        return disparity >= self.fairness_thresholds.get('max_disparity',0.8)

    def validate_latency(self, latency_samples):
        p95 = np.percentile(latency_samples,95)
        self.validation_results['latency']={'p95': p95}
        return p95 <= self.latency_threshold

def main():
    # In real scenario: Load model predictions, latency samples, etc.
    # Here we mock them for demonstration.
    y_true = np.array([0,1,1,0])
    y_pred = np.array([0,1,1,0])
    y_prob = np.array([0.2,0.9,0.85,0.1])
    subgroup_scores = {'priv':0.95,'unpriv':0.8}
    latency_samples = [0.1,0.12,0.3,0.45,0.5]

    validator = ModelValidator(
        performance_thresholds={'accuracy':0.9,'f1':0.8},
        fairness_thresholds={'max_disparity':0.8},
        latency_threshold=0.5
    )

    if not validator.validate_performance(y_true,y_pred,y_prob):
        print("Performance validation failed.")
        sys.exit(1)
    if not validator.validate_fairness(subgroup_scores):
        print("Fairness validation failed.")
        sys.exit(1)
    if not validator.validate_latency(latency_samples):
        print("Latency validation failed.")
        sys.exit(1)

    print("All validations passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
