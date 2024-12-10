"""
handle_imbalance.py

Class imbalance can mislead metrics like accuracy. This snippet adjusts class weights
to give minority classes a fair representation, improving performance metrics that
reflect real-world priorities.

Key concepts:
- Handling imbalanced classification
- Using class_weight to improve minority class performance
"""

import numpy as np
from sklearn.utils import class_weight

def adjust_class_weights(pipeline, X_train, y_train):
    """
    Compute balanced class weights and apply them to the classifier in the pipeline.
    Ensures fairer treatment of minority classes.

    Args:
        pipeline: The sklearn pipeline with a classifier supporting class_weight.
        X_train: Training features
        y_train: Training labels

    Returns:
        pipeline with updated class_weight parameter.
    """
    cw = class_weight.compute_class_weight(
        'balanced', classes=np.unique(y_train), y=y_train)
    # Assuming the last step in the pipeline is 'clf'
    if hasattr(pipeline['clf'], 'class_weight'):
        pipeline['clf'].set_params(class_weight=dict(enumerate(cw)))
        print("Class weights adjusted for imbalance.")
    else:
        print("This classifier does not support class_weight.")
    return pipeline
