import requests

img_path = r"C:\Users\kano\.gemini\antigravity-ide\brain\40433e41-6606-43ba-bf42-0c7fce6f4905\.user_uploaded\media_1789288148046.png"

with open(img_path, "rb") as f:
    files = {"file": ("user_apple_leaf.png", f, "image/png")}
    res = requests.post("http://127.0.0.1:5144/api/disease/predict", files=files)

data = res.json()
print("HTTP Unconstrained:", data["label"], f"{data['confidence']*100:.2f}%")
for r in data.get("crop_refinements", []):
    print(f"  * Refinement suggested: {r['display_name']} - {r['disease_name']} ({r['conditioned_confidence']*100:.2f}%)")

with open(img_path, "rb") as f:
    files = {"file": ("user_apple_leaf.png", f, "image/png")}
    res_cond = requests.post("http://127.0.0.1:5144/api/disease/predict", files=files, data={"crop_filter": "apple"})

data_cond = res_cond.json()
print("HTTP Apple Conditioned:", data_cond["label"], f"{data_cond['confidence']*100:.2f}%")
print("HTTP Conditioned Filter Applied:", data_cond.get("crop_filter_applied"))
print("Grad-CAM length:", len(data_cond.get("gradcam_b64") or ""))
assert data_cond["label"] == "Apple___Cedar_apple_rust"
assert data_cond["confidence"] > 0.85
print("ALL LIVE HTTP CHECKS PASSED 100%!")
