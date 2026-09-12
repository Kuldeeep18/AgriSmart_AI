import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import csv
from collections import defaultdict
from utils.disease_model import predict_leaf_disease

VAL_DIR = "data/val"
METRICS_CSV = "artifacts/public_plantvillage_baseline/evaluation/per_class_metrics.csv"
CLASS_NAMES_JSON = "artifacts/public_plantvillage_baseline/class_names.json"

with open(CLASS_NAMES_JSON, "r", encoding="utf-8") as f:
    classes = json.load(f)

# Load metrics
class_metrics = {}
if os.path.exists(METRICS_CSV):
    with open(METRICS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            class_metrics[row["label"]] = row

results = []
grouped_by_crop = defaultdict(list)

print(f"Testing real sample images for all {len(classes)} classes across all supported fruits & vegetables:\n")

for idx, cls in enumerate(classes, 1):
    cls_dir = os.path.join(VAL_DIR, cls)
    if not os.path.exists(cls_dir):
        print(f"[{idx:02d}/38] MISSING DIR: {cls}")
        continue
    
    files = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not files:
        print(f"[{idx:02d}/38] NO IMAGES: {cls}")
        continue
    
    sample_file = files[0]
    sample_path = os.path.join(cls_dir, sample_file)
    with open(sample_path, "rb") as fp:
        payload = fp.read()
    
    res = predict_leaf_disease(payload)
    pred_label = res.get("label", "ERROR")
    conf = res.get("confidence", 0.0)
    matched = (pred_label == cls)
    
    # Parse crop name
    parts = cls.split("___")
    crop_name = parts[0].replace("_", " ").replace("(", "").replace(")", "").strip()
    disease_name = parts[1].replace("_", " ").strip() if len(parts) > 1 else "healthy"
    
    metric = class_metrics.get(cls, {})
    f1 = float(metric.get("f1", 0.0)) * 100
    support = int(float(metric.get("support", len(files))))
    
    item = {
        "index": idx,
        "crop": crop_name,
        "condition": disease_name,
        "class_id": cls,
        "sample_file": sample_file,
        "predicted_label": pred_label,
        "confidence_pct": round(conf * 100, 2),
        "validation_f1_pct": round(f1, 2),
        "val_images_count": support,
        "matched": matched
    }
    results.append(item)
    grouped_by_crop[crop_name].append(item)
    
    status_icon = "MATCH" if matched else "DIFF"
    print(f"[{idx:02d}/38] [{status_icon}] {crop_name:22s} | {disease_name:35s} | Conf: {conf*100:5.1f}% | Val-F1: {f1:5.1f}%")

with open("scratch/every_crop_audit.json", "w", encoding="utf-8") as fp:
    json.dump({"total_classes": len(classes), "results": results}, fp, indent=2)

print(f"\nCompleted audit of all {len(classes)} classes across {len(grouped_by_crop)} unique crops!")
