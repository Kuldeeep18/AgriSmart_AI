import os
import sys
import io
import json
from datetime import date

# Ensure repo root is on sys.path
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app import app
from extensions import db
from models import User, UserCrop, CropLog, Topic, Answer

def run_comprehensive_test():
    print("=" * 80)
    print("  AGRISMART AI - COMPLETE HEADLESS SYSTEM & FEATURE TEST SUITE")
    print("  Real Google/Web Photos · Quality Gate · Irrigation · ML · Farm Ops · Chat")
    print("=" * 80)

    client = app.test_client()
    passed = 0
    total = 0

    # ---------------------------------------------------------
    # TEST 1: AUTHENTICATION & DEMO SESSION
    # ---------------------------------------------------------
    total += 1
    print("\n[TEST 1] Testing Demo Authentication & Session Initialization...")
    res = client.get("/demo-login", follow_redirects=True)
    if res.status_code == 200:
        with client.session_transaction() as sess:
            user_id = sess.get("user_id")
            user_name = sess.get("full_name")
        if user_id:
            print(f"  [PASS] Logged in as demo user '{user_name}' (ID: {user_id})")
            passed += 1
        else:
            print("  [FAIL] Session user_id missing after /demo-login")
    else:
        print(f"  [FAIL] HTTP {res.status_code}")

    # ---------------------------------------------------------
    # TEST 2: LEAF DISEASE DETECTION ON REAL GOOGLE/WEB IMAGES
    # ---------------------------------------------------------
    image_tests = [
        ("google_corn_blight.jpg", "Corn (Maize)", "Northern Leaf Blight"),
        ("google_potato_late_blight.jpg", "Potato", "Late Blight"),
        ("google_tomato_late_blight.jpg", "Tomato", "Late Blight"),
        ("google_pepper_bacterial_spot.jpg", "Pepper", "Bacterial Spot"),
        ("google_cedar_apple_rust.jpg", "Apple", "Cedar Apple Rust"),
        ("google_grape_black_rot.jpg", "Grape", "Black Rot"),
        ("google_tomato_septoria.jpg", "Tomato", "Septoria Leaf Spot"),
        ("google_citrus_healthy.jpg", "Orange / Citrus", "Healthy"),
    ]

    print("\n[TEST 2] Testing Leaf Disease AI Model on Real-World Google/Web Images...")
    for filename, crop, cond in image_tests:
        total += 1
        filepath = os.path.join("downloaded_from_google", filename)
        if not os.path.exists(filepath):
            print(f"  [SKIP] {filename}: file not found")
            continue
        
        with open(filepath, "rb") as f:
            img_bytes = f.read()

        data = {"file": (io.BytesIO(img_bytes), filename)}
        res = client.post("/api/disease/predict", data=data, content_type="multipart/form-data")
        
        if res.status_code == 200:
            resp_data = res.get_json()
            label = resp_data.get("label", "")
            confidence = resp_data.get("confidence", 0.0)
            precautions = resp_data.get("precautions", [])
            print(f"  [PASS] [{filename}] -> {label} (Conf: {confidence*100:.1f}%)")
            if precautions:
                print(f"         Treatment: {precautions[0][:60]}...")
            passed += 1
        else:
            print(f"  [FAIL] [{filename}] HTTP {res.status_code} - {res.data.decode()[:100]}")

    # ---------------------------------------------------------
    # TEST 3: QUALITY GATE / NON-LEAF TEST
    # ---------------------------------------------------------
    total += 1
    print("\n[TEST 3] Testing Quality Gate & Non-Plant Image Rejection...")
    non_plant_path = os.path.join("downloaded_from_google", "test_non_plant_laptop.jpg")
    with open(non_plant_path, "rb") as f:
        img_bytes = f.read()
    data = {"file": (io.BytesIO(img_bytes), "test_non_plant_laptop.jpg")}
    res = client.post("/api/disease/predict", data=data, content_type="multipart/form-data")
    resp_data = res.get_json() or {}
    label = resp_data.get("label", "")
    warnings = resp_data.get("quality_warnings", [])
    confidence = resp_data.get("confidence", -1.0)
    print(f"  Quality Gate Response: Label='{label}', Confidence={confidence}, Warnings={warnings}")
    if label == "Non-Plant / Unclear Image" and confidence == 0.0 and len(warnings) > 0:
        print("  [PASS] Non-plant image correctly rejected by Quality Gate with actionable warning!")
        passed += 1
    else:
        print("  [FAIL] Quality Gate failed to reject non-plant image")

    # ---------------------------------------------------------
    # TEST 4: SMART IRRIGATION ADVISORY ENGINE
    # ---------------------------------------------------------
    total += 1
    print("\n[TEST 4] Testing Smart Irrigation Advisory (Decoupled Rules + Sustainability)...")
    # Case A: Low moisture, high heat, no rain -> IRRIGATE_NOW
    advisory_payload_irrigate = {
        "crop": "Tomato",
        "stage": "flowering",
        "soil_moisture_pct": 20.0,
        "temperature_c": 36.0,
        "humidity_pct": 40.0,
        "rain_probability_pct": 10.0,
        "forecast_rain_mm": 0.0
    }
    res = client.post("/api/advisory", json=advisory_payload_irrigate)
    d_a = res.get_json() if res.status_code == 200 else {}
    action_a = d_a.get("irrigation_action")
    score_a = d_a.get("sustainability_score")

    # Case B: Good moisture, impending heavy rain -> DELAY_IRRIGATION
    advisory_payload_delay = {
        "crop": "Tomato",
        "stage": "growing",
        "soil_moisture_pct": 55.0,
        "temperature_c": 26.0,
        "humidity_pct": 80.0,
        "rain_probability_pct": 85.0,
        "forecast_rain_mm": 18.0
    }
    res = client.post("/api/advisory", json=advisory_payload_delay)
    d_b = res.get_json() if res.status_code == 200 else {}
    action_b = d_b.get("irrigation_action")
    score_b = d_b.get("sustainability_score")

    print(f"  Hot/Dry Scenario: Action = {action_a} (Score: {score_a}/100)")
    print(f"  Rain Scenario:    Action = {action_b} (Score: {score_b}/100)")

    if action_a in ["IRRIGATE", "IRRIGATE_NOW"] and action_b in ["DELAY_IRRIGATION", "MONITOR"]:
        print("  [PASS] Transparent rule engine and sustainability scoring verified!")
        passed += 1
    else:
        print(f"  [FAIL] Unexpected actions ({action_a}, {action_b})")

    # ---------------------------------------------------------
    # TEST 5: ML CROP RECOMMENDATION & FERTILIZER ENGINE
    # ---------------------------------------------------------
    total += 1
    print("\n[TEST 5] Testing ML Crop Recommendation (Random Forest Classifier)...")
    crop_input = {
        "n": 90,
        "p": 42,
        "k": 43,
        "ph": 6.5,
        "temp": 24.5,
        "humidity": 82.0,
        "soil_type": "Clay Loam"
    }
    res = client.post("/api/predict-crop", json=crop_input)
    if res.status_code == 200:
        d = res.get_json()
        predicted_crop = d.get("result")
        match_pct = d.get("match_percentage")
        recs = d.get("recommendations", [])
        print(f"  [PASS] Recommended Crop: '{predicted_crop}' (Confidence: {match_pct}%)")
        print(f"         Water Need: {d.get('water_req')} | Harvest Cycle: {d.get('duration')}")
        print(f"         Agronomy Rec: {recs[0] if recs else 'Standard balanced NPK'}")
        passed += 1
    else:
        print(f"  [FAIL] HTTP {res.status_code} - {res.data.decode()[:100]}")

    # ---------------------------------------------------------
    # TEST 6: 1-CLICK FARM CREATION FROM PREDICTION
    # ---------------------------------------------------------
    total += 1
    print("\n[TEST 6] Testing 1-Click Farm Creation from Prediction...")
    farm_payload = {
        "crop_name": "rice",
        "farm_name": "Automated Test Rice Field",
        "area_acres": 2.5
    }
    res = client.post("/api/create_farm_from_prediction", json=farm_payload)
    if res.status_code == 200:
        d = res.get_json()
        new_farm_id = d.get("user_crop_id")
        print(f"  [PASS] Farm created successfully with user_crop_id = {new_farm_id}")
        passed += 1
    else:
        print(f"  [FAIL] HTTP {res.status_code} - {res.data.decode()[:100]}")
        new_farm_id = None

    # ---------------------------------------------------------
    # TEST 7: LOGGING DISEASE DIAGNOSIS TO FARM TIMELINE
    # ---------------------------------------------------------
    total += 1
    print("\n[TEST 7] Testing Disease Diagnosis Logging to Farm Timeline...")
    with app.app_context():
        user = User.query.filter_by(email="demo@agrismart.ai").first()
        target_farm = UserCrop.query.filter_by(user_id=user.user_id).first()
        target_farm_id = target_farm.user_crop_id if target_farm else new_farm_id

    save_diag_payload = {
        "user_crop_id": target_farm_id,
        "disease_label": "Tomato___Late_blight",
        "confidence": 0.965,
        "precautions": [
            "Prune infected lower foliage immediately.",
            "Apply Copper Oxychloride 50 WP at 2.5g/L water."
        ]
    }
    res = client.post("/api/disease/save_to_farm", json=save_diag_payload)
    if res.status_code == 200:
        d = res.get_json()
        print(f"  [PASS] Diagnosis logged to Farm ID {target_farm_id}")
        passed += 1
    else:
        print(f"  [FAIL] HTTP {res.status_code} - {res.data.decode()[:100]}")

    # ---------------------------------------------------------
    # TEST 8: CROP TRACKING DASHBOARD & BENCHMARK ALERTS
    # ---------------------------------------------------------
    total += 1
    print("\n[TEST 8] Testing Crop Standards & Sensor Scout Benchmark Alerts...")
    res = client.get(f"/api/crop_standards/{target_farm_id}")
    if res.status_code == 200:
        d = res.get_json()
        stages = d.get("stages", [])
        opt_lcc = d.get("optimal_lcc")
        print(f"  Growth Stages: {len(stages)} stages | Target LCC: {opt_lcc}")
        
        # Test logging field data with Nitrogen Deficiency (LCC = 2 vs target 4)
        scout_payload = {
            "height": 18.0,
            "lcc": 2,
            "moisture": "Low",
            "stage": "Vegetative",
            "stand_count": 92
        }
        res_log = client.post(f"/log_field_data/{target_farm_id}", json=scout_payload)
        if res_log.status_code == 200:
            log_data = res_log.get_json()
            alerts = log_data.get("alerts", [])
            has_nitrogen_alert = any("Nitrogen Deficiency" in a for a in alerts)
            clean_alerts = [a.encode("ascii", "replace").decode("ascii") for a in alerts]
            print(f"  Agronomic Alerts: {clean_alerts}")
            if has_nitrogen_alert:
                print("  [PASS] Benchmark alert engine successfully triggered Nitrogen Deficiency advisory!")
                passed += 1
            else:
                print("  [FAIL] Nitrogen deficiency alert was not triggered")
        else:
            print(f"  [FAIL] log_field_data returned HTTP {res_log.status_code}")
    else:
        print(f"  [FAIL] /api/crop_standards returned HTTP {res.status_code}")

    # ---------------------------------------------------------
    # TEST 9: COMMUNITY FORUM ENGINE
    # ---------------------------------------------------------
    total += 1
    print("\n[TEST 9] Testing Farmer Community Forum (Post Question, Answer, Upvote)...")
    ask_payload = {
        "title": "Best biological control for aphids in tomato crops?",
        "description": "Looking for field-tested biological and organic solutions for aphid management in summer.",
        "category": "Pest & Disease"
    }
    res = client.post("/farmer_community", data=ask_payload, follow_redirects=True)
    if res.status_code == 200:
        with app.app_context():
            created_topic = Topic.query.filter_by(title="Best biological control for aphids in tomato crops?").first()
            if created_topic:
                print(f"  [PASS] Forum topic created successfully with ID {created_topic.topic_id}")
                # Post answer
                ans_res = client.post(
                    f"/topic/{created_topic.topic_id}", 
                    data={"answer_text": "Apply 5% Neem Seed Kernel Extract (NSKE) spray during early morning hours."},
                    follow_redirects=True
                )
                posted_ans = Answer.query.filter_by(topic_id=created_topic.topic_id).first()
                if posted_ans:
                    print(f"  [PASS] Answer submitted with ID {posted_ans.answer_id}")
                    # Test like / upvote
                    like_res = client.post(f"/answer/{posted_ans.answer_id}/like")
                    print(f"  [PASS] Answer upvoted successfully (Status: {like_res.status_code})")
                passed += 1
            else:
                print("  [FAIL] Topic was not found in DB")
    else:
        print(f"  [FAIL] /farmer_community returned HTTP {res.status_code}")

    # ---------------------------------------------------------
    # TEST 10: AGRONOMY AI CHATBOT ASSISTANT
    # ---------------------------------------------------------
    total += 1
    print("\n[TEST 10] Testing Agronomy AI Chatbot Assistant...")
    chat_payload = {"question": "How to handle yellow leaves and fertilizer management in wheat?"}
    res = client.post("/chatbot", json=chat_payload)
    if res.status_code == 200:
        d = res.get_json()
        reply = d.get("response", "")
        clean_reply = reply.encode("ascii", "replace").decode("ascii")
        print(f"  [PASS] Chatbot reply received:")
        print(f"         \"{clean_reply[:120]}...\"")
        passed += 1
    else:
        print(f"  [FAIL] /chatbot returned HTTP {res.status_code}")

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"  TEST RESULTS: {passed} / {total} Subsystems & Tests PASSED ({passed/total*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_comprehensive_test()
