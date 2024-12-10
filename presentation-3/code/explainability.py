"""
explainability.py

Integrates SHAP to explain model predictions. By understanding which features
drive decisions, we ensure our models are not just black boxes. This visibility
supports compliance with explainability regulations and fosters trust with stakeholders.

Key concepts:
- SHAP for interpreting model predictions
- Identifying potential biases or spurious correlations
- Enhancing stakeholder confidence in model decisions
"""

import shap

def explain_predictions(pipeline, X_train, X_val):
    """
    Generate SHAP explanations for sample predictions from the validation set.

    Args:
        pipeline: A trained sklearn pipeline (must be compatible with SHAP explainer chosen).
        X_train: Training features, needed for SHAP background data.
        X_val: Validation features to explain.

    Returns:
        SHAP values for a sample of the validation data.
    """
    # Example: Using LinearExplainer, suitable if pipeline ends in a linear model
    explainer = shap.LinearExplainer(pipeline['clf'], X_train)
    shap_values = explainer.shap_values(X_val[:1])
    # The shap.force_plot can be shown in Jupyter or saved as HTML
    # shap.force_plot(explainer.expected_value, shap_values, X_val.iloc[0])
    print("SHAP explanations computed for a sample prediction.")
    return shap_values
