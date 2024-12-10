"""
entity_based_split.py

For tasks like user-level predictions, ensuring the model generalizes to completely
new entities (users, items) is crucial. Entity-based splits ensure no entity overlap
between training and validation, reducing the risk of data leakage.

Key concepts:
- Entity-based splitting
- Testing model generalization beyond known entities
"""

import pandas as pd

def entity_based_split(df: pd.DataFrame, known_entities: list, entity_col='entity_id') -> (pd.DataFrame, pd.DataFrame):
    """
    Split data into training and validation sets based on known vs unknown entities.

    Args:
        df (pd.DataFrame): The dataset containing an entity identifier column.
        known_entities (list): List of entity IDs to include in training set.
        entity_col (str): The name of the entity identifier column.

    Returns:
        (pd.DataFrame, pd.DataFrame): Training and validation subsets with no entity overlap.

    Raises:
        KeyError: If entity_col not in df.
    """
    if entity_col not in df.columns:
        raise KeyError(f"Entity column '{entity_col}' not found in DataFrame.")

    df_train = df[df[entity_col].isin(known_entities)]
    df_val = df[~df[entity_col].isin(known_entities)]

    # Sanity check: no overlap in entities
    overlap = set(df_train[entity_col]) & set(df_val[entity_col])
    if overlap:
        raise RuntimeError("Entity overlap detected between training and validation sets.")

    print(f"Entity-based split done. Train entities: {df_train[entity_col].nunique()}, "
          f"Val entities: {df_val[entity_col].nunique()}")

    return df_train, df_val
