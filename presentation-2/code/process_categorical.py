"""
process_categorical.py

This script encodes categorical features using one-hot encoding, handling unknown categories
to prevent runtime errors. It ensures a uniform, transparent representation of categorical
data, reducing bias and improving model interpretability.

Key concepts:
- One-hot encoding
- Handling unknown categories
- Maintaining consistent categorical feature spaces
"""

import pandas as pd
from sklearn.preprocessing import OneHotEncoder

def process_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    One-hot encode categorical columns, handle unknown categories gracefully.

    Args:
        df (pd.DataFrame): The dataset with categorical columns.

    Returns:
        pd.DataFrame: Dataset with categorical columns replaced by encoded features.
    """
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) == 0:
        print("No categorical columns to encode.")
        return df

    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoded = encoder.fit_transform(df[categorical_cols])
    encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols))

    # Drop original categorical columns and append encoded features
    df = pd.concat([df.drop(columns=categorical_cols), encoded_df], axis=1)
    print(f"Categorical columns encoded: {list(categorical_cols)}")
    return df
