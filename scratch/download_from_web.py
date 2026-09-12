import os
import re
import json
import urllib.request
import urllib.parse
from PIL import Image

OUT_DIR = "downloaded_from_google"
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_image_urls(query, limit=5):
    try:
        url = f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8")
        
        match = re.search(r'vqd=([\d-]+)', html)
        if not match:
            match = re.search(r'vqd=["\']([\d-]+)["\']', html)
        if not match:
            return []
        
        token = match.group(1)
        api_url = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={urllib.parse.quote(query)}&vqd={token}"
        req2 = urllib.request.Request(api_url, headers=HEADERS)
        with urllib.request.urlopen(req2, timeout=8) as resp2:
            data = json.loads(resp2.read().decode("utf-8"))
        
        return [r["image"] for r in data.get("results", []) if "image" in r][:limit]
    except Exception as e:
        print(f"Search error for {query}: {e}")
        return []

def download_and_verify(image_url, save_path):
    try:
        req = urllib.request.Request(image_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        
        if len(data) < 5000:
            return False
        
        with open(save_path, "wb") as f:
            f.write(data)
        
        # Verify it's a valid image with PIL
        with Image.open(save_path) as img:
            img.verify()
        return True
    except Exception as e:
        # cleanup if corrupt
        if os.path.exists(save_path):
            try: os.remove(save_path)
            except: pass
        return False

# Target crops to search on Google/Web
SEARCH_TARGETS = [
    ("google_cedar_apple_rust.jpg", "cedar apple rust leaf disease spots"),
    ("google_grape_black_rot.jpg", "grape black rot leaf lesion"),
    ("google_corn_common_rust.jpg", "corn common rust leaf pustules"),
    ("google_tomato_septoria.jpg", "tomato septoria leaf spot disease"),
    ("google_peach_bacterial_spot.jpg", "peach bacterial spot leaf Xanthomonas")
]

print("Searching Google/Web for real crop leaf disease images:\n")

downloaded_files = []
for filename, query in SEARCH_TARGETS:
    print(f"Querying web: '{query}'...")
    urls = get_image_urls(query, limit=6)
    saved = False
    save_path = os.path.join(OUT_DIR, filename)
    for u in urls:
        if download_and_verify(u, save_path):
            size_kb = os.path.getsize(save_path) / 1024
            print(f"  [SUCCESS] Saved {filename} ({size_kb:.1f} KB) from {u[:60]}...")
            downloaded_files.append((filename, query))
            saved = True
            break
    if not saved:
        print(f"  [FAILED] Could not download a valid image for '{query}'")

print(f"\nSuccessfully downloaded {len(downloaded_files)} real images from web search!")
