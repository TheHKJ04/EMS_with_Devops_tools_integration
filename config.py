import os


class Config:
    """Runtime configuration loaded from environment variables."""

    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    APP_NAME = "Employee Management System"
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "uploads")

    # This must be a Werkzeug-generated password hash, not a plaintext password.
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH")

    DEBUG = False
