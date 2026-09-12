import requests

targets = [
    ("google_grape_black_rot.jpg", "downloaded_from_google/google_grape_black_rot.jpg"),
    ("google_tomato_septoria.jpg", "downloaded_from_google/google_tomato_septoria.jpg"),
    ("online_potato_blight.jpg", "downloaded_test_leaves/online_potato_blight.jpg"),
    ("online_tomato_early_blight.jpg", "downloaded_test_leaves/online_tomato_early_blight.jpg")
]

print("=== VERIFYING HTTP API INFERENCE ON DOWNLOADED LEAVES ===\n")
for name, path in targets:
    with open(path, "rb") as fp:
        res = requests.post("http://127.0.0.1:5144/api/disease/predict", files={"file": fp})
    data = res.json()
    print(f"File: {name} (HTTP {res.status_code})")
    print(f"  Predicted Label: {data.get('label')}")
    print(f"  Confidence: {data.get('confidence', 0.0)*100:.2f}%")
    print(f"  Treatment: {data.get('precautions', ['None'])[0]}")
    print("-" * 60)
