"""
privacy_protection.py

This snippet demonstrates a simple pseudonymization step: hashing sensitive fields.
True anonymization requires more steps, but this is a starting point.

Key concepts:
- Privacy by design
- Protecting sensitive user identifiers
- Laying groundwork for compliance (e.g., GDPR)
"""

import hashlib
import pandas as pd

def pseudonymize_column(series: pd.Series) -> pd.Series:
    """
    Hash column values using SHA-256 for pseudonymization.
    """
    return series.apply(lambda x: hashlib.sha256(str(x).encode()).hexdigest())

def protect_privacy(df: pd.DataFrame, sensitive_cols=['user_id','email','phone_number']) -> pd.DataFrame:
    """
    Pseudonymize specified sensitive columns and remove original fields.

    Args:
        df (pd.DataFrame): The dataset.
        sensitive_cols (list): Columns to pseudonymize.

    Returns:
        pd.DataFrame: Dataset with hashed columns replacing sensitive fields.
    """
    for col in sensitive_cols:
        if col in df.columns:
            df[col+"_hashed"] = pseudonymize_column(df[col])
            df = df.drop(columns=[col])
    print("Sensitive columns pseudonymized:", sensitive_cols)
    return df
