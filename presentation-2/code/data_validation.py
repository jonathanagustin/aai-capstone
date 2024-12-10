"""
data_validation.py

This script uses Pandera to validate the dataset against a defined schema.
By enforcing constraints on columns (e.g., age ranges, income >= 0), we ensure
data integrity and reduce the risk of passing invalid or unethical data
downstream.

Key concepts:
- Pandera for schema validation
- Early detection of anomalies
- Providing clear error messages and halting pipeline if validation fails
"""

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series

class InputSchema(pa.SchemaModel):
    age: Series[int] = pa.Field(ge=0, le=120)
    income: Series[float] = pa.Field(ge=0)

    class Config:
        strict = True
        coerce = True

def validate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate the dataset against the InputSchema. Raises an error if validation fails.

    Args:
        df (pd.DataFrame): The dataset to validate.

    Returns:
        pd.DataFrame: The validated dataset, if successful.

    Raises:
        RuntimeError: If validation fails.
    """
    try:
        validated = InputSchema.validate(df)
        print("Validation passed: Dataset meets all schema constraints.")
        return validated
    except pa.errors.SchemaError as e:
        print("Validation failed:", str(e))
        raise RuntimeError("Data validation failed") from e
