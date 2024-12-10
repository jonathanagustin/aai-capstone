# generate_model_card.py
"""
generate_model_card.py

Generates a model card in JSON format after model training or updates.
This card includes performance metrics, fairness results, dataset info, intended use, limitations,
and ethical considerations. The card is then archived by the CI pipeline for auditing and compliance.

Key concepts:
- Transparency of model capabilities
- Enabling stakeholders to understand and contest decisions
- Documenting ethical considerations
"""

import json

def generate_model_card(model_name, performance, fairness, dataset_info):
    card = {
        "model_name": model_name,
        "performance": performance,
        "fairness": fairness,
        "dataset_info": dataset_info,
        "intended_use": "Classifier for domain X",
        "limitations": "Limited testing on low-resource languages",
        "ethical_considerations": "Potential bias in underrepresented groups"
    }
    return card

if __name__ == "__main__":
    # Mock metrics and info for demonstration
    perf={"accuracy":0.93,"f1":0.90}
    fair={"max_disparity":0.1}
    data={"source":"internal_v4","size":60000}

    card=generate_model_card("my_model_v3",perf,fair,data)
    with open("model_card.json","w") as f:
        json.dump(card,f,indent=2)
    print("Model card generated and saved as model_card.json.")
