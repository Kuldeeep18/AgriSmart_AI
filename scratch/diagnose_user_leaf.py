import os, sys
sys.path.insert(0, os.path.abspath("."))
from utils.disease_model import predict_leaf_disease
img_path = r"C:\Users\kano\.gemini\antigravity-ide\brain\40433e41-6606-43ba-bf42-0c7fce6f4905\.user_uploaded\media_1789288148046.png"

with open(img_path, "rb") as f:
    raw_bytes = f.read()

print("="*70)
print("TEST 1: AUTO-DETECT (UNCONSTRAINED) WITH SMART DISAMBIGUATION")
print("="*70)
res_auto = predict_leaf_disease(raw_bytes)
print("Label:       ", res_auto.get("label"))
print("Confidence:  ", f"{res_auto.get('confidence', 0)*100:.2f}%")
print("TTA Enhanced:", res_auto.get("is_tta"))
print("Alternatives:")
for alt in res_auto.get("alternatives", []):
    print(f"  - {alt.get('label')}: {alt.get('confidence')*100:.2f}%")
print("Smart Refinements Suggested:")
for ref in res_auto.get("crop_refinements", []):
    print(f"  * {ref.get('crop')} -> {ref.get('top_label')} ({ref.get('conditioned_confidence')*100:.2f}% match)")

print("\n" + "="*70)
print("TEST 2: APPLE-CONDITIONED PREDICTION (USER CHOOSES APPLE OR REFINES)")
print("="*70)
res_apple = predict_leaf_disease(raw_bytes, crop_filter="apple")
print("Label:       ", res_apple.get("label"))
print("Confidence:  ", f"{res_apple.get('confidence', 0)*100:.2f}%")
print("Filter Applied:", res_apple.get("crop_filter_applied"))
print("TTA Enhanced:", res_apple.get("is_tta"))
print("Alternatives:")
for alt in res_apple.get("alternatives", []):
    print(f"  - {alt.get('label')}: {alt.get('confidence')*100:.2f}%")
print("Grad-CAM b64 present:", bool(res_apple.get("gradcam_b64")))
print("="*70)

