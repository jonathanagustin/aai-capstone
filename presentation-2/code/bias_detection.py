"""
bias_detection.py

This snippet measures bias using AIF360 and applies a pre-processing mitigation
technique (Reweighing). Actual mitigation strategies depend on your context and
the bias types encountered.

Key concepts:
- Measuring disparate impact
- Statistical parity difference
- Reweighing to adjust instance weights before training
"""

import pandas as pd
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import BinaryLabelDatasetMetric
from aif360.algorithms.preprocessing import Reweighing

def mitigate_bias(df: pd.DataFrame, label_col='decision', protected_attributes=['gender','race']) -> pd.DataFrame:
    """
    Measure and mitigate bias in the dataset. Applies a reweighing technique to
    ensure more equitable distribution of weights.

    Args:
        df (pd.DataFrame): The dataset with a binary label and protected attributes.
        label_col (str): The label column name.
        protected_attributes (list): Protected attribute names.

    Returns:
        pd.DataFrame: Transformed dataset with mitigated bias via reweighing.
    """
    dataset = BinaryLabelDataset(
        df=df,
        label_names=[label_col],
        protected_attribute_names=protected_attributes
    )

    privileged_groups = [{'gender':1}]
    unprivileged_groups = [{'gender':0}]

    metrics = BinaryLabelDatasetMetric(
        dataset,
        unprivileged_groups=unprivileged_groups,
        privileged_groups=privileged_groups
    )
    print("Initial Disparate Impact:", metrics.disparate_impact())
    print("Initial Statistical Parity Difference:", metrics.statistical_parity_difference())

    # Apply Reweighing
    reweighing = Reweighing(
        unprivileged_groups=unprivileged_groups,
        privileged_groups=privileged_groups
    )
    transformed_dataset = reweighing.fit_transform(dataset)

    # Return transformed dataset as DataFrame
    return transformed_dataset.convert_to_dataframe()[0]
