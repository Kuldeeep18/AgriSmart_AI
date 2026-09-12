from __future__ import annotations

import argparse
import io
import json
import threading
from dataclasses import dataclass
from pathlib import Path


class ModelNotConfiguredError(RuntimeError):
    pass


@dataclass(frozen=True)
class Prediction:
    label: str
    confidence: float
    alternatives: list[dict[str, float | str]]


class ArtifactPredictor:
    """Thread-safe, lazy loader for an explicitly versioned PyTorch artifact."""

    def __init__(self, weights_path: str | Path, class_names_path: str | Path, architecture: str = "efficientnet_b0") -> None:
        self.weights_path, self.class_names_path = Path(weights_path), Path(class_names_path)
        self.architecture = architecture
        self._model = self._classes = self._transform = None
        self._lock = threading.Lock()

    @property
    def is_configured(self) -> bool:
        return self.weights_path.is_file() and self.class_names_path.is_file()

    def _load(self) -> None:
        if self._model is not None:
            return
        if not self.is_configured:
            raise ModelNotConfiguredError("No trained AgriSmart artifact is configured. Train the official-label model first.")
        import torch
        from torchvision.models import efficientnet_b0, mobilenet_v2
        from torchvision.transforms import v2

        with self._lock:
            if self._model is None:
                self._classes = json.loads(self.class_names_path.read_text(encoding="utf-8"))
                if self.architecture == "efficientnet_b0":
                    model = efficientnet_b0(weights=None)
                elif self.architecture == "mobilenet_v2":
                    model = mobilenet_v2(weights=None)
                else:
                    raise ModelNotConfiguredError(f"Unsupported artifact architecture: {self.architecture}")
                model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, len(self._classes))
                model.load_state_dict(torch.load(self.weights_path, map_location="cpu", weights_only=True))
                model.eval()
                self._model = model
                normalise = v2.Normalize([0.0, 0.0, 0.0], [1.0, 1.0, 1.0]) if self.architecture == "mobilenet_v2" else v2.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
                self._transform = v2.Compose([v2.Resize((224, 224)), v2.ToImage(), v2.ToDtype(torch.float32, scale=True), normalise])

    def predict_bytes(self, payload: bytes) -> Prediction:
        self._load()
        import torch
        from PIL import Image

        image = Image.open(io.BytesIO(payload)).convert("RGB")
        tensor = self._transform(image).unsqueeze(0)
        with torch.inference_mode():
            probabilities = torch.softmax(self._model(tensor)[0], dim=0)
        top = torch.topk(probabilities, k=min(3, len(self._classes)))
        alternatives = [{"label": self._classes[index], "confidence": round(float(score), 4)} for score, index in zip(top.values, top.indices)]
        return Prediction(label=alternatives[0]["label"], confidence=alternatives[0]["confidence"], alternatives=alternatives)


_default_predictor = ArtifactPredictor("artifacts/current/best_model.pt", "artifacts/current/class_names.json")


def predict(image_path: str) -> str:
    """Required single-image contract: returns the exact trained label string."""
    return _default_predictor.predict_bytes(Path(image_path).read_bytes()).label


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--weights", default="artifacts/current/best_model.pt")
    parser.add_argument("--class-names", default="artifacts/current/class_names.json")
    args = parser.parse_args()
    result = ArtifactPredictor(args.weights, args.class_names).predict_bytes(Path(args.image).read_bytes())
    print(json.dumps({"label": result.label, "confidence": result.confidence, "alternatives": result.alternatives}))
