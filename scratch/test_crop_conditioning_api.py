import io
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from app import app

client = app.test_client()
img_path = r"C:\Users\kano\.gemini\antigravity-ide\brain\40433e41-6606-43ba-bf42-0c7fce6f4905\.user_uploaded\media_1789288148046.png"

with open(img_path, "rb") as f:
    img_bytes = f.read()

print("=" * 80)
print("  TEST 1: API /api/disease/predict (AUTO-DETECT / UNCONSTRAINED)")
print("=" * 80)
data = {"file": (io.BytesIO(img_bytes), "user_apple_leaf.png")}
res = client.post("/api/disease/predict", data=data, content_type="multipart/form-data")
assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.data}"
res_json = res.get_json()

print(f"Status Code:      {res.status_code}")
print(f"Predicted Label:  {res_json.get('label')}")
print(f"Confidence:       {res_json.get('confidence')*100:.2f}%")
print(f"TTA Enabled:      {res_json.get('is_tta')}")
print(f"Grad-CAM Heatmap: {'Present (' + str(len(res_json.get('gradcam_b64', '') or '')) + ' chars)' if res_json.get('gradcam_b64') else 'None'}")
print(f"Crop Refinements: {res_json.get('crop_refinements')}")
assert res_json.get("crop_refinements"), "Expected crop_refinements in response!"
ref = res_json["crop_refinements"][0]
print(f"  -> Disambiguation Suggestion: {ref['display_name']} - {ref['disease_name']} ({ref['conditioned_confidence']*100:.2f}% match)")
assert ref["crop_key"] == "apple", f"Expected apple refinement, got {ref['crop_key']}"

print("\n" + "=" * 80)
print("  TEST 2: API /api/disease/predict WITH crop_filter='apple' (1-CLICK REFINEMENT)")
print("=" * 80)
data_apple = {
    "file": (io.BytesIO(img_bytes), "user_apple_leaf.png"),
    "crop_filter": "apple"
}
res2 = client.post("/api/disease/predict", data=data_apple, content_type="multipart/form-data")
assert res2.status_code == 200, f"Expected 200, got {res2.status_code}: {res2.data}"
res2_json = res2.get_json()

print(f"Status Code:        {res2.status_code}")
print(f"Predicted Label:    {res2_json.get('label')}")
print(f"Confidence:         {res2_json.get('confidence')*100:.2f}%")
print(f"Filter Applied:     {res2_json.get('crop_filter_applied')}")
print(f"TTA Enabled:        {res2_json.get('is_tta')}")
print(f"Grad-CAM Heatmap:   {'Present (' + str(len(res2_json.get('gradcam_b64', '') or '')) + ' chars)' if res2_json.get('gradcam_b64') else 'None'}")
print("Top-3 Alternatives:")
for alt in res2_json.get("alternatives", []):
    print(f"  - {alt.get('label')}: {alt.get('confidence')*100:.2f}%")

assert res2_json.get("label") == "Apple___Cedar_apple_rust", f"Expected Cedar Apple Rust, got {res2_json.get('label')}"
assert res2_json.get("confidence") > 0.80, f"Expected >80% confidence, got {res2_json.get('confidence')}"
assert res2_json.get("crop_filter_applied") == "Apple"
assert res2_json.get("gradcam_b64"), "Grad-CAM must be generated for the refined disease"

print("\n" + "=" * 80)
print("  ALL API TESTS PASSED PERFECTLY! [100% SUCCESS]")
print("=" * 80)
