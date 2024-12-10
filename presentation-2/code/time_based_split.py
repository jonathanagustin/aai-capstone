"""
time_based_split.py

This script demonstrates time-based data splitting for training and validation sets.
Following Rachel Thomas's recommendations, we ensure that the validation set represents
future data, providing a more realistic assessment of the model's real-world performance.

Key concepts:
- Time-based splitting
- Preventing overly optimistic estimates from random splits
"""

import pandas as pd

def time_based_split(df: pd.DataFrame, cutoff: str, val_end: str) -> (pd.DataFrame, pd.DataFrame):
    """
    Split the DataFrame into training and validation sets based on a temporal cutoff.

    Args:
        df (pd.DataFrame): The dataset containing a 'date' column.
        cutoff (str): The date string used as a cutoff for training data.
        val_end (str): The end date for the validation period.

    Returns:
        (pd.DataFrame, pd.DataFrame): Training and validation subsets.

    Raises:
        KeyError: If 'date' column not found.
    """
    if 'date' not in df.columns:
        raise KeyError("DataFrame must contain a 'date' column for time-based splitting.")

    df_train = df[df['date'] <= cutoff]
    df_val = df[(df['date'] > cutoff) & (df['date'] <= val_end)]

    print(f"Time-based split:")
    print(f"Training cutoff: {cutoff}, Validation end: {val_end}")
    print(f"Train samples: {len(df_train)}, Validation samples: {len(df_val)}")

    return df_train, df_val
