import io
import ipaddress
import os
from urllib.error import URLError
from urllib.request import urlopen
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from utils.disease_model import predict_leaf_disease, get_active_predictor
from fieldguard.services.advisory import irrigation_advice, sustainability_score
from fieldguard.schemas import SensorContext

disease_bp = Blueprint("disease_detection", __name__)
MAX_UPLOAD_BYTES = 8 * 1024 * 1024

@disease_bp.route("/disease_detection")
def disease_detection():
    predictor, model_mode, model_notice = get_active_predictor()
    return render_template(
        "Disease_Detection/disease_detection.html",
        model_mode=model_mode,
        model_notice=model_notice
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
