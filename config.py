import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database URL: uses PostgreSQL if configured, otherwise falls back to local SQLite database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///biogrow.db"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY", "biogrow-secret-key-2026-secure-session")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in ("true", "1", "yes")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")  # Required by Flask-Mail
