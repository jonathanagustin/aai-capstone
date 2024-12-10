"""
data_loading.py

This script loads a dataset from a CSV file and identifies which columns are numeric
and which are categorical. This separation is a foundational step in building a robust,
ethical ML data preprocessing pipeline.

Key concepts:
- Data loading from a CSV
- Initial inspection of column types
- Lays groundwork for automated preprocessing
"""

import pandas as pd

def load_and_inspect_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file and print the count of numeric and categorical columns.

    Args:
        file_path (str): Path to the CSV file containing the raw data.

    Returns:
        pd.DataFrame: The loaded dataset as a pandas DataFrame.

    Raises:
        FileNotFoundError: If the provided file path does not exist.
    """
    df = pd.read_csv(file_path)
    print(f"Data loaded from {file_path}, shape: {df.shape}")

    numeric_cols = df.select_dtypes(include=['float','int']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    print(f"Numeric columns: {len(numeric_cols)} -> {list(numeric_cols)}")
    print(f"Categorical columns: {len(categorical_cols)} -> {list(categorical_cols)}")

    return df
