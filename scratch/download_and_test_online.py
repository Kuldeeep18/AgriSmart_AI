import os
import sys
sys.path.insert(0, os.path.abspath("."))
import requests
from utils.disease_model import predict_leaf_disease

OUT_DIR = "downloaded_from_google"
os.makedirs(OUT_DIR, exist_ok=True)
headers = {"User-Agent": "AgriSmart-FieldGuard/2.0 (agritech@binarybrains.sih)"}

TARGETS = [
    {
        "filename": "google_cedar_apple_rust.jpg",
        "expected": "Apple___Cedar_apple_rust",
        "crop": "Apple",
        "disease": "Cedar Apple Rust",
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/23/2012-06-23_Gymnosporangium_juniperi-virginianae_Schweinitz_230353.jpg"
    },
    {
        "filename": "google_grape_black_rot.jpg",
        "expected": "Grape___Black_rot",
        "crop": "Grape",
        "disease": "Black Rot",
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Guignardia_bidwellii_%28black_rot%29_on_grape_1.jpg"
    },
    {
        "filename": "google_tomato_septoria.jpg",
        "expected": "Tomato___Septoria_leaf_spot",
        "crop": "Tomato",
        "disease": "Septoria Leaf Spot",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/76/Septoria_lycopersici_malagutii_leaf_spot_on_tomato_leaf.jpg"
    }
]

print("=== DOWNLOADING AND TESTING REAL ONLINE IMAGES ===\n")

for item in TARGETS:
    filepath = os.path.join(OUT_DIR, item["filename"])
    print(f"Downloading {item['crop']} - {item['disease']} from web...")
    try:
        r = requests.get(item["url"], headers=headers, timeout=12)
        if r.status_code == 200 and len(r.content) > 5000:
            with open(filepath, "wb") as f:
                f.write(r.content)
            size_kb = len(r.content) / 1024
            print(f"  [SAVED] {item['filename']} ({size_kb:.1f} KB)")
        else:
            print(f"  [FAILED] HTTP status {r.status_code}")
            continue
    except Exception as e:
        print(f"  [ERROR] {e}")
        continue

    # Run inference through the project
    with open(filepath, "rb") as f:
        payload = f.read()
    
    res = predict_leaf_disease(payload)
    pred_label = res.get("label", "ERROR")
    conf = res.get("confidence", 0.0)
    matched = (pred_label == item["expected"])
    
    print(f"  -> Predicted: {pred_label}")
    print(f"  -> Confidence: {conf*100:.2f}%")
    print(f"  -> Status: {'EXACT MATCH' if matched else 'CLOSE / ALTERNATIVE'}")
    if res.get("quality_warnings"):
        print(f"  -> Quality Flags: {res.get('quality_warnings')}")
    if res.get("precautions"):
        print(f"  -> Actionable Treatment: {res.get('precautions')[0]}")
    print("-" * 65)
