from typing import Dict


def run_mock_inference(image_path: str) -> Dict:
    # deterministic mock
    return {
        "disease": "leaf_blight",
        "confidence": 0.87,
        "treatment": "Apply copper-based fungicide and improve drainage.",
    }
