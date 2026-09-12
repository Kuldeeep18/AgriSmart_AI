import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
from utils.disease_model import predict_leaf_disease

files = [
    'online_tomato_early_blight.jpg',
    'online_tomato_late_blight.jpg',
    'online_potato_blight.jpg',
    'online_healthy_tomato.jpg'
]

print("Starting inference on newly downloaded images from the web:\n")
for f in files:
    path = os.path.join('downloaded_test_leaves', f)
    if not os.path.exists(path):
        continue
    with open(path, 'rb') as fp:
        payload = fp.read()
    res = predict_leaf_disease(payload)
    print(f"File: {f} ({len(payload)} bytes)")
    print(f"  Predicted Label: {res.get('label')}")
    conf = res.get('confidence', 0.0)
    print(f"  Confidence: {conf*100:.2f}%")
    print(f"  Quality Warnings: {res.get('quality_warnings')}")
    if res.get('alternatives'):
        print(f"  Top Alternatives: {res.get('alternatives')[:2]}")
    if res.get('precautions'):
        print(f"  Actionable Treatment: {res.get('precautions')[0]}")
    print("-" * 60)
