# AgriSmart AI — FieldGuard

An original, farmer-first crop-disease detection system designed for the SIH-2026 lab-to-field challenge. The disease classifier is the source of truth; farm context only enriches the advice and cannot alter the predicted disease.

## Modules

- **Core:** transfer-learning disease classifier, one-image `predict` interface, confidence and precautions.
- **Farmer scan UX:** upload, browser-camera capture, and a private-network ESP32-CAM `/capture` integration.
- **Evaluation:** macro-F1, accuracy, per-class precision/recall, and raw/normalised confusion matrices.
- **Bonus-ready advisory:** validated sensor input, weather-aware irrigation rule trace, and reproducible sustainability score.

## Quick start

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. The UI and API start without a database. A trained artifact is required for predictions.

For a runnable local UI before the official dataset arrives, the app automatically converts the locally cloned reference's H5 model into a PyTorch **legacy demo** artifact. Every response from that path is marked `legacy_reference_demo`; it is not compliant for SIH metrics, labels, or submission claims.

## Data contract

The official kickoff dataset is not committed. Create `data/train/<exact organizer label>/...` and `data/val/<exact organizer label>/...`. The provided held-out field test set must **never** be supplied to `model/train.py`; it is evaluated only through the prediction interface. Do not rename or invent class labels: use the kickoff registry verbatim.

## Train, evaluate, predict

```powershell
py -m model.train --train-dir data/train --val-dir data/val --output-dir artifacts/run-001
py -m model.evaluate --weights artifacts/run-001/best_model.pt --class-names artifacts/run-001/class_names.json --data-dir data/val --output-dir artifacts/run-001/evaluation
py -m model.predict --image path\to\leaf.jpg --weights artifacts/run-001/best_model.pt --class-names artifacts/run-001/class_names.json
```

`predict(image_path)` in `model/predict.py` is the reproducible single-image interface. The evaluator is for a permitted labelled validation/public-format set; organizer-held-out results must be reported only when actually returned by the organizers.

## Public baseline data

For the local baseline, this project uses the public [PlantVillage Dataset](https://github.com/spMohanty/PlantVillage-Dataset), specifically `raw/color`. `model/prepare_plantvillage.py` makes an 80/20 deterministic stratified split with seed `2026`, recording it in `data/public_baseline_manifest.json`. This split evaluates lab-condition images only; it is not the competition's PlantDoc-style field holdout and must not be represented as such.

## References and originality

Reference repositories are cloned locally under `.references/` and excluded from the submission. Their code is not copied. This implementation independently applies the useful concepts identified in [the audit](docs/REPOSITORY_AUDIT.md): safe lazy inference, a farmer scan workflow, validated sensor context, and transparent policies. It does not reuse their model weights, label maps, frontend, or database code.

Known limitation: model performance cannot be claimed until the official data is available and a run is evaluated. See `report/MODEL_REPORT.md` for the required reporting template.
