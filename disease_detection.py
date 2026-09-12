import io
import ipaddress
import os
from urllib.error import URLError
from urllib.request import urlopen
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from datetime import date
import json

from extensions import db
from models import UserCrop, CropLog
from utils.disease_model import predict_leaf_disease, get_active_predictor
from fieldguard.services.advisory import irrigation_advice, sustainability_score
from fieldguard.schemas import SensorContext

disease_bp = Blueprint("disease_detection", __name__)
MAX_UPLOAD_BYTES = 8 * 1024 * 1024

@disease_bp.route("/disease_detection")
def disease_detection():
    predictor, model_mode, model_notice = get_active_predictor()
    user_crops = []
    if "user_id" in session:
        user_crops = UserCrop.query.filter_by(user_id=session["user_id"]).all()
        
    return render_template(
        "Disease_Detection/disease_detection.html",
        model_mode=model_mode,
        model_notice=model_notice,
        user_crops=user_crops
    )

@disease_bp.route("/api/disease/predict", methods=["POST"])
def api_predict():
    if "file" not in request.files:
        return jsonify({"error": "No image file provided in upload."}), 400
        
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Selected file is empty."}), 400

    payload = file.read()
    if len(payload) > MAX_UPLOAD_BYTES:
        return jsonify({"error": "Image size exceeds the 8 MB limit."}), 413

    result = predict_leaf_disease(payload)
    if "error" in result:
        return jsonify(result), 422
        
    return jsonify(result)

@disease_bp.route("/api/disease/esp32", methods=["POST"])
def api_esp32_capture():
    data = request.get_json() or {}
    host = data.get("host", "").strip()
    
    if not host:
        return jsonify({"error": "ESP32 IP address is required."}), 400

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return jsonify({"error": "Enter a valid private IP address (e.g. 192.168.1.50) without http:// or port."}), 422

    if not (address.is_private or address.is_loopback):
        return jsonify({"error": "ESP32-CAM must use a private local network IP address."}), 422

    try:
        with urlopen(f"http://{address.compressed}/capture", timeout=5) as response:
            payload = response.read(MAX_UPLOAD_BYTES + 1)
    except (URLError, OSError, TimeoutError) as exc:
        return jsonify({"error": f"Could not capture image from ESP32-CAM: {str(exc)}"}), 502

    result = predict_leaf_disease(payload)
    if "error" in result:
        return jsonify(result), 422
        
    return jsonify(result)

@disease_bp.route("/api/advisory", methods=["POST"])
def api_advisory():
    data = request.get_json() or {}
    try:
        context = SensorContext(
            crop=data.get("crop", "Tomato"),
            stage=data.get("stage", "growing"),
            soil_moisture_pct=float(data.get("soil_moisture_pct", 30)),
            temperature_c=float(data.get("temperature_c", 28)),
            humidity_pct=float(data.get("humidity_pct", 65)),
            rain_probability_pct=float(data.get("rain_probability_pct", 20)),
            forecast_rain_mm=float(data.get("forecast_rain_mm", 0))
        )
        action, reason, trace = irrigation_advice(context)
        score = sustainability_score(context, action)
        
        return jsonify({
            "irrigation_action": action,
            "reason": reason,
            "sustainability_score": score,
            "trace": trace + ["Disease classification is strictly decoupled from environmental irrigation heuristics."]
        })
    except Exception as e:
        return jsonify({"error": f"Advisory evaluation failed: {str(e)}"}), 400

@disease_bp.route("/api/disease/save_to_farm", methods=["POST"])
def api_save_to_farm():
    if "user_id" not in session:
        return jsonify({"error": "Please log in to record diagnostic logs to your farm."}), 401
        
    data = request.get_json() or {}
    user_crop_id = data.get("user_crop_id")
    if not user_crop_id:
        return jsonify({"error": "Please select an active farm."}), 400
        
    user_crop = UserCrop.query.filter_by(user_crop_id=user_crop_id, user_id=session["user_id"]).first()
    if not user_crop:
        return jsonify({"error": "Selected farm was not found."}), 404
        
    disease_label = data.get("disease_label", "Healthy Crop Leaf")
    confidence = float(data.get("confidence", 0.0))
    precautions = data.get("precautions", [])
    
    today = date.today()
    crop_log = CropLog.query.filter_by(user_crop_id=user_crop.user_crop_id, log_date=today).first()
    calc_week = int((today - user_crop.sowing_date).days / 7) + 1
    if calc_week < 1:
        calc_week = 1
        
    is_healthy = "healthy" in disease_label.lower()
    status_val = "healthy" if is_healthy else "active_disease"
    
    if not crop_log:
        crop_log = CropLog(
            user_crop_id=user_crop.user_crop_id,
            log_date=today,
            week_number=calc_week,
            disease_label=disease_label,
            disease_confidence=confidence,
            disease_precautions_json=json.dumps(precautions),
            disease_status=status_val
        )
        db.session.add(crop_log)
    else:
        crop_log.disease_label = disease_label
        crop_log.disease_confidence = confidence
        crop_log.disease_precautions_json = json.dumps(precautions)
        crop_log.disease_status = status_val
        
    try:
        from community import award_points
        award_points(session["user_id"], 10, f"Logged foliage diagnosis for {user_crop.farm_name}")
    except Exception:
        pass
        
    db.session.commit()
    return jsonify({
        "success": True,
        "message": f"Successfully logged '{disease_label}' to {user_crop.farm_name}! (+10 Farm Health Points)",
        "farm_name": user_crop.farm_name,
        "points_awarded": 10
    })
