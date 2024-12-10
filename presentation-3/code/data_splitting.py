"""
data_splitting.py

Splitting data into train, validation, and test sets ensures unbiased model evaluation.
Stable test sets and representative distributions help maintain trust in reported performance.

Key concepts:
- Avoiding data leakage
- Maintaining consistent evaluation protocols
"""

from sklearn.model_selection import train_test_split

def split_data(X, y, test_size=0.2, val_size=0.25):
    """
    Split data into train, validation, and test sets.

    Args:
        X: Features
        y: Labels
        test_size (float): Proportion of data to reserve for testing.
        val_size (float): Proportion of remaining data to reserve for validation.

    Returns:
        X_train, X_val, X_test, y_train, y_val, y_test
    """
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=test_size)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=val_size)
    print("Data split complete.")
    return X_train, X_val, X_test, y_train, y_val, y_test
