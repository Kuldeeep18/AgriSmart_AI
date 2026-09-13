import os
import requests
from PIL import Image

OUT_DIR = "downloaded_from_google"
os.makedirs(OUT_DIR, exist_ok=True)

headers = {
    "User-Agent": "AgriSmart-FieldGuard/2.0 (agritech@binarybrains.sih; +http://localhost:5144)"
}

DOWNLOAD_TARGETS = [
    {
        "filename": "google_corn_blight.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/2/2d/Northern_corn_leaf_blight.JPG",
        "crop": "Corn (Maize)",
        "condition": "Northern Leaf Blight"
    },
    {
        "filename": "google_peach_leaf_curl.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/1/16/Leaf_curl_on_peach.jpg",
        "crop": "Peach",
        "condition": "Leaf curl / Bacterial Spot"
    },
    {
        "filename": "google_potato_late_blight.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/1/14/Phytophthora_infestans_on_potato_leaf.jpg",
        "crop": "Potato",
        "condition": "Late Blight"
    },
    {
        "filename": "google_tomato_late_blight.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/04/Tomato_late_blight_leaf_curl_2_%285816171413%29.jpg",
        "crop": "Tomato",
        "condition": "Late Blight"
    },
    {
        "filename": "google_pepper_bacterial_spot.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Bacterial_leaf_spot_of_pepper_%28Capsicum_sp.%29_%2843614805831%29.jpg",
        "crop": "Pepper Bell",
        "condition": "Bacterial Spot"
    },
    {
        "filename": "google_citrus_healthy.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Citrus_leaf%28crop%29.jpg",
        "crop": "Orange / Citrus",
        "condition": "Citrus Leaf"
    },
    {
        "filename": "google_non_leaf_car.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/40/1954_Sunbeam_Talbot_Alpine_sports_roadster_at_Capel_Manor%2C_Enfield%2C_London%2C_England_2.jpg",
        "crop": "Non-Plant Object",
        "condition": "Vintage Car (Quality Gate Rejection Test)"
    }
]

print("=== DOWNLOADING REAL RANDOM CROP & CONTROL IMAGES FROM WEB ===")
for item in DOWNLOAD_TARGETS:
    filepath = os.path.join(OUT_DIR, item["filename"])
    print(f"Downloading [{item['crop']}] - {item['condition']}...")
    try:
        r = requests.get(item["url"], headers=headers, timeout=20)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(filepath, "wb") as f:
                f.write(r.content)
            # verify image
            with Image.open(filepath) as img:
                img.verify()
            size_kb = len(r.content) / 1024
            print(f"  [SAVED & VERIFIED] {item['filename']} ({size_kb:.1f} KB)")
        else:
            print(f"  [ERROR] Status code: {r.status_code}")
    except Exception as e:
        print(f"  [ERROR] {e}")

print("\nFinished downloading test set!")
