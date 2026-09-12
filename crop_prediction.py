import json
import os
from flask import Blueprint, render_template, request, jsonify, make_response, session, flash, redirect, url_for
from extensions import db
from models import CropStandard, PredictionReport
from utils.prediction_model import get_prediction, recommend_fertilizer
from utils.water_requirements import crop_water_requirements

crop_prediction_bp = Blueprint("crop_prediction", __name__)

@crop_prediction_bp.route("/crop_prediction")
def crop_prediction():
    return render_template("Crop_Prediction/crop_prediction.html")

@crop_prediction_bp.route("/api/predict-crop", methods=["POST"])
def predict_crop():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    try:
        n = float(data.get("n", 0))
        p = float(data.get("p", 0))
        k = float(data.get("k", 0))
        ph = float(data.get("ph", 6.5))
        temp = float(data.get("temp", 25.0))
        humidity = float(data.get("humidity", 60.0))
        soil_type = str(data.get("soil_type", "Alluvial Soil"))

        result, match_percentage = get_prediction(n, p, k, ph, temp, humidity, soil_type)
        recommendations = recommend_fertilizer(result, n, p, k)

        standard = CropStandard.query.filter_by(crop_name=result.lower()).first()
        duration_str = "90 - 120 days"
        duration_list = [90, 120]
        if standard and standard.growth_config:
            total_days = standard.growth_config.get("total_duration_days", [90, 120])
            if isinstance(total_days, list) and len(total_days) >= 2:
                duration_str = f"{total_days[0]} - {total_days[1]} days"
                duration_list = total_days

        water_req = crop_water_requirements.get(result.lower(), "Moderate (450 - 650 mm)")

        user_id = session.get("user_id")
        new_report = PredictionReport(
            user_id=user_id,
            n=n, p=p, k=k,
            ph=ph, humidity=humidity,
            temperature=temp, soil_type=soil_type,
            crop_name=result,
            match_percentage=float(match_percentage),
            water_req=water_req,
            harvest_duration=duration_str,
            recommendations_json=json.dumps(recommendations)
        )
        
        db.session.add(new_report)
        db.session.commit()

        return jsonify({
            "result": result,
            "match_percentage": match_percentage,
            "recommendations": recommendations,
            "duration": duration_list,
            "water_req": water_req,
            "report_id": new_report.report_id
        })
    
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": "Invalid numeric format for N, P, K, pH, Temperature or Humidity."}), 400
    except Exception as e:
        return jsonify({"error": f"Prediction computation failed: {str(e)}"}), 500


@crop_prediction_bp.route('/download_report/<int:report_id>', methods=['GET'])
def download_report(report_id):
    report = PredictionReport.query.get_or_404(report_id)

    if session.get("user_id") and report.user_id and report.user_id != session.get("user_id"):
        return jsonify({"error": "Unauthorized access to report."}), 403
    
    try:
        recs = json.loads(report.recommendations_json) if report.recommendations_json else []
    except Exception:
        recs = []

    data_for_pdf = {
        "report_date": report.created_at.strftime("%Y-%m-%d %H:%M"),
        "report_id": report.report_id,
        "current_year": report.created_at.year,
        "inputs": {
             "n": report.n, "p": report.p, "k": report.k, 
             "ph": report.ph, "temp": report.temperature, 
             "humidity": report.humidity, "soil_type": report.soil_type
        },
        "result": {
            "crop_name": report.crop_name,
            "match_percentage": report.match_percentage,
            "water_requirement": report.water_req,
            "harvest_duration": report.harvest_duration,
            "recommendations": recs
        }
    }

    rendered_html = render_template('pdf_report.html', **data_for_pdf)
    
    # Try generating PDF with pdfkit if available
    try:
        import pdfkit
        wkhtml_path = os.getenv("PATH_WKHTMLTOPDF")
        config = pdfkit.configuration(wkhtmltopdf=wkhtml_path) if wkhtml_path else None
        pdf = pdfkit.from_string(rendered_html, False, configuration=config)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=BioGrow_{report.crop_name.capitalize()}_Report.pdf'
        return response
    except Exception:
        # Graceful printable HTML response
        return rendered_html
