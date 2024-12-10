# AI Masters Capstone Project

This repository houses a series of presentations, code snippets, and supporting materials demonstrating how to build a comprehensive, automated, and ethically grounded machine learning (ML) pipeline. The content is structured into five key presentations, each exploring different phases of the ML lifecycle—from data handling and training to deployment automation, code quality, and ethical governance.

## Video Presentations

Video presentations are available in Vimeo in [here](https://vimeo.com/showcase/11489928).

## Contents

```plaintext
.
├── presentation-1
│   ├── presentation-1.tex
│   └── presentation-1.pdf
├── presentation-2
│   ├── code
│   │   ├── bias_detection.py
│   │   ├── data_loading.py
│   │   ├── data_validation.py
│   │   ├── entity_based_split.py
│   │   ├── privacy_protection.py
│   │   ├── process_categorical.py
│   │   ├── process_numeric.py
│   │   └── time_based_split.py
│   ├── presentation-2.tex
│   └── presentation-2.pdf
├── presentation-3
│   ├── code
│   │   ├── automate_training.py
│   │   ├── data_splitting.py
│   │   ├── explainability.py
│   │   ├── fairness_check.py
│   │   ├── handle_imbalance.py
│   │   ├── hyperparameter_optimization.py
│   │   └── model_versioning.py
│   ├── presentation-3.tex
│   └── presentation-3.pdf
├── presentation-4
│   ├── code
│   │   ├── ci_cd_workflow.yaml
│   │   ├── Dockerfile
│   │   ├── health_check.py
│   │   ├── k8s_deployment.yaml
│   │   ├── model_validator.py
│   │   ├── monitoring.py
│   │   └── rollback_manager.py
│   ├── presentation-4.tex
│   └── presentation-4.pdf
├── presentation-5
│   ├── code
│   │   ├── cd_cd_cosign.yml
│   │   ├── ci_cd_codeql.yml
│   │   ├── ci_cd_lint_workflow.yml
│   │   ├── ci_cd_model_card.yml
│   │   ├── ci_cd_snyk.yml
│   │   ├── generate_model_card.py
│   │   └── PULL_REQUEST_TEMPLATE.md
│   ├── presentation-5.tex
│   └── presentation-5.pdf
└── README.md
```

## Overview of Each Presentation

1. **Presentation 1: Introduction & Ethical Foundations**
   - Lays out the ethical, legal, and compliance imperatives for ML development.
   - Explores foundational legal cases and the necessity of trustworthy, transparent, and fair ML pipelines.

2. **Presentation 2: Data Preparation & Ethical Data Handling**
   - Demonstrates automated, ethical preprocessing techniques: validation, privacy protection, bias detection, and handling time-based/entity-based splits.
   - Emphasizes data quality, compliance with regulations (e.g., GDPR), and embedding fairness from the start.

3. **Presentation 3: Automating Training & Ensuring Fairness**
   - Shows how to automate model training pipelines, integrate hyperparameter optimization, and track experiments with MLflow.
   - Details the use of explainability tools (SHAP/LIME) and fairness checks to ensure continuous oversight.

4. **Presentation 4: Deployment Automation & Compliance**
   - Covers production-level MLOps practices: CI/CD with bias checks, Docker and Kubernetes for scalable, reproducible deployments.
   - Introduces monitoring, automated rollback strategies, and compliance checks to maintain trust and performance in production environments.

5. **Presentation 5: Code Quality, Security & Ethical Governance**
   - Focuses on code quality, security scanning (Snyk, CodeQL), and attestation (Cosign) to prevent malicious exploitation.
   - Discusses automating documentation (model cards), ethical PR templates, and governance frameworks to ensure long-term adherence to ethical standards.

## Code Structure & Purpose

- **`presentation-2/code`**: Scripts demonstrating data loading, validation, privacy enforcement, categorical and numeric processing, and bias detection.
- **`presentation-3/code`**: Automation of training steps, hyperparameter optimization, explainability, fairness checks, and model versioning.
- **`presentation-4/code`**: CI/CD pipelines, Docker optimization, Kubernetes deployment configs, model validation scripts, monitoring integrations, and rollback logic.
- **`presentation-5/code`**: Security scanning, attestation workflows, linting and code quality checks, model card generation, and PR templates for ethical review.

Each code snippet is documented to explain its ethical or compliance-related function. They serve as reference implementations for integrating fairness, transparency, privacy, and compliance checks throughout the ML lifecycle.

## Getting Started

1. **Exploring Code**:
   Each `code` directory contains Python scripts or YAML workflows illustrating best practices. Feel free to review them for guidance on integrating ethics, fairness, and compliance into your ML projects.

1. **Adapting to Your Project**:
   The patterns shown—such as using `pandera` for data validation, `aif360` for fairness checks, `mlflow` for experiment tracking, `Snyk` and `CodeQL` for security scanning, and `cosign` for supply chain attestation—are adaptable to your context. Integrate them incrementally, ensuring each step aligns with your legal and ethical obligations.

## References

- [FTC Guidelines](https://www.ftc.gov/)
- [AIF360 Toolkit](https://github.com/Trusted-AI/AIF360)
- [Pandera Library](https://pandera.readthedocs.io/)
- [GDPR](https://gdpr.eu/)
- [Rachel Thomas (2017): Validation Sets](https://rachel.fast.ai/posts/2017-11-13-validation-sets/)