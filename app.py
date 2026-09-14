import os
import random
from datetime import datetime, timedelta
import requests
from flask import Flask, redirect, request, url_for, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

# ================= CONFIG & EXTENSIONS =================
from config import Config
from extensions import db, mail

# ================= APP INIT =================
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail.init_app(app)

# ================= MODELS =================
from models import User, Otp, Answer, Topic, CropStandard

# ================= BLUEPRINTS =================
from chatbot import chatbot_bp
from crop_prediction import crop_prediction_bp
from crop_tracking import crop_tracking_bp
from auth import auth_bp
from community import community_bp, give_daily_bonus
from disease_detection import disease_bp

app.register_blueprint(chatbot_bp)
app.register_blueprint(crop_prediction_bp)
app.register_blueprint(crop_tracking_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(community_bp)
app.register_blueprint(disease_bp)

from utils.avtar import get_initials


# ================= INITIALIZE DB & SEED DATA =================
with app.app_context():
    db.create_all()
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            if "sqlite" not in str(db.engine.url):
                conn.execute(text("""
                    ALTER TABLE crop_logs ADD COLUMN IF NOT EXISTS disease_label VARCHAR(100);
                    ALTER TABLE crop_logs ADD COLUMN IF NOT EXISTS disease_confidence FLOAT;
                    ALTER TABLE crop_logs ADD COLUMN IF NOT EXISTS disease_precautions_json TEXT;
                    ALTER TABLE crop_logs ADD COLUMN IF NOT EXISTS disease_status VARCHAR(50) DEFAULT 'active';
                """))
                conn.commit()
    except Exception:
        pass

    try:
        # Check if CropStandards are seeded
        if CropStandard.query.count() == 0:
            from seed_crops import seed_database
            seed_database()
        
        # Check if Demo User is seeded
        if User.query.filter_by(email="demo@agrismart.ai").count() == 0:
            from seed_demo_data import seed_demo_platform
            seed_demo_platform()
    except Exception as e:
        print(f"[BioGrow Warning] Seed database check: {e}")


# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("HomePage/home_page.html")


# ---------------- DEMO LOGIN ----------------
@app.route("/demo-login")
def demo_login():
    demo_user = User.query.filter_by(email="demo@agrismart.ai").first()
    if not demo_user:
        from seed_demo_data import seed_demo_platform
        seed_demo_platform()
        demo_user = User.query.filter_by(email="demo@agrismart.ai").first()

    session["user_id"] = demo_user.user_id
    session["full_name"] = demo_user.full_name
    session["initials"] = get_initials(demo_user.full_name)
    session["location"] = demo_user.location
    session["badge"] = demo_user.badge
    give_daily_bonus(demo_user.user_id)
    flash(f"Welcome back, {demo_user.full_name}! 🌾", "success")
    return redirect(url_for("crop_tracking.crop_tracking"))


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    now = datetime.now()
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            if not user.is_verified:
                Otp.query.filter_by(
                    user_id=user.user_id,
                    is_used=False
                ).update({"is_used": True})

                generated_otp = str(random.randint(100000, 999999))
                otp = Otp(
                    user_id=user.user_id,
                    otp_code=generated_otp,
                    expires_at=now + timedelta(minutes=10),
                    is_used=False
                )
                db.session.add(otp)
                db.session.commit()

                from utils.mailer import send_otp_email
                send_otp_email(user.email, generated_otp, user.full_name)
                return redirect(url_for("verify_otp", user_id=user.user_id))

            session["user_id"] = user.user_id
            session["full_name"] = user.full_name
            session["initials"] = get_initials(user.full_name)
            session["location"] = user.location
            session["badge"] = user.badge
            give_daily_bonus(user.user_id)
            
            flash(f"Welcome back, {user.full_name}! 🌾", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for('login'))

    return render_template("Login/login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_record = User.query.get(session["user_id"])
    if not user_record:
        session.clear()
        return redirect(url_for("login"))

    if not user_record.is_verified:
        return redirect(url_for("verify_otp", user_id=user_record.user_id))

    # 🌤 WEATHER LOGIC
    api_key = os.getenv("WEATHER_API")
    city = user_record.location or "Delhi"

    weather_data = None
    if api_key and city:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
            response = requests.get(url, timeout=4)
            if response.status_code == 200:
                data = response.json()
                weather_data = {
                    "temp": round(data["main"]["temp"]),
                    "humidity": data["main"]["humidity"],
                    "description": data["weather"][0]["description"].capitalize()
                }
        except Exception:
            pass

    if not weather_data:
        weather_data = {
            "temp": 28,
            "humidity": 65,
            "description": "Clear Sky / Mild Sunshine"
        }

    return render_template(
        "Dashboard/dashboard.html",
        user=user_record,
        weather=weather_data
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been safely logged out.", "info")
    return redirect(url_for("login"))


# ---------------- OTP VERIFY ----------------
@app.route("/verify-otp/<int:user_id>", methods=["GET", "POST"])
def verify_otp(user_id):
    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        now = datetime.now()

        otp_record = (
            Otp.query
            .filter(
                Otp.user_id == user_id,
                Otp.is_used == False
            )
            .order_by(Otp.created_at.desc())
            .first()
        )

        if not otp_record or otp_record.otp_code != entered_otp:
            return render_template(
                "Otp/verify_otp.html",
                error="Invalid OTP code. Please check and retry.",
                user_id=user_id
            )

        if otp_record.expires_at < now:
            return render_template(
                "Otp/verify_otp.html",
                error="OTP has expired. Please click Resend OTP.",
                user_id=user_id
            )

        otp_record.is_used = True
        user = User.query.get(user_id)
        if user:
            user.is_verified = True
            db.session.commit()
            session["user_id"] = user.user_id
            session["full_name"] = user.full_name
            session["initials"] = get_initials(user.full_name)
            session["location"] = user.location
            session["badge"] = user.badge
            give_daily_bonus(user.user_id)
            flash("Account verified successfully! Welcome to BioGrow.", "success")
            return redirect(url_for("dashboard"))

        return redirect(url_for("login"))

    return render_template("Otp/verify_otp.html", user_id=user_id)


# ---------------- RESEND OTP ----------------
@app.route("/resend-otp/<int:user_id>")
def resend_otp(user_id):
    user = User.query.get(user_id)
    if not user:
        flash("Invalid user request.", "danger")
        return redirect(url_for("login"))
    
    if user.is_verified:
        return redirect(url_for("login"))

    Otp.query.filter_by(user_id=user_id, is_used=False).update(
        {"is_used": True}
    )

    now = datetime.now()
    new_otp = str(random.randint(100000, 999999))
    otp = Otp(
        user_id=user_id,
        otp_code=new_otp,
        expires_at=now + timedelta(minutes=10),
        is_used=False
    )

    db.session.add(otp)
    db.session.commit()

    from utils.mailer import send_otp_email
    send_otp_email(user.email, new_otp, user.full_name)
    flash("A new verification code has been dispatched to your email.", "info")
    return redirect(url_for("verify_otp", user_id=user_id))


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        location = request.form.get("location", "").strip()
        dob_str = request.form.get("dob", "")
        mobile = request.form.get("mobile", "").strip()

        if User.query.filter_by(email=email).first():
            flash("Email address is already registered. Please login.", "warning")
            return redirect(url_for("login"))

        dob_val = None
        if dob_str:
            try:
                dob_val = datetime.strptime(dob_str, "%Y-%m-%d").date()
            except ValueError:
                dob_val = None

        user = User(
            full_name=full_name,
            email=email,
            password_hash=generate_password_hash(password),
            role="FARMER",
            points=10,  # Welcome bonus points
            lifetime_points=10,
            badge="Beginner",
            location=location,
            dob=dob_val,
            mobile=mobile,
            is_verified=False,
            created_at=datetime.now()
        )

        db.session.add(user)
        db.session.commit()

        otp_code = str(random.randint(100000, 999999))
        otp = Otp(
            user_id=user.user_id,
            otp_code=otp_code,
            expires_at=datetime.now() + timedelta(minutes=10),
            is_used=False
        )

        db.session.add(otp)
        db.session.commit()

        from utils.mailer import send_otp_email
        send_otp_email(user.email, otp_code, user.full_name)
        flash("Registration successful! Please verify your OTP.", "success")
        return redirect(url_for("verify_otp", user_id=user.user_id))
    
    return render_template("Login/login.html")


# ---------------- PROFILE & BADGES ----------------
BADGE_ORDER = [
    ("Beginner", 0),
    ("Contributor", 50),
    ("Trusted Farmer", 150),
    ("Expert Farmer", 300),
]

def get_next_badge_info(lifetime_points):
    for badge, points in BADGE_ORDER:
        if lifetime_points < points:
            return badge, points
    return "Max Level (Expert Farmer)", None


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    if not user:
        return redirect(url_for("login"))

    question_count = Topic.query.filter_by(user_id=user.user_id).count()
    answers_count = Answer.query.filter_by(user_id=user.user_id).count()
    best_answers_count = Answer.query.filter_by(
        user_id=user.user_id,
        is_best_solution=True
    ).count()
    next_badge, next_badge_points = get_next_badge_info(user.lifetime_points)

    return render_template(
        "Profile/profile.html",
        user=user,
        question_count=question_count,
        answers_count=answers_count,
        best_answers_count=best_answers_count,
        next_badge=next_badge,
        next_badge_points=next_badge_points
    )


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5144)
