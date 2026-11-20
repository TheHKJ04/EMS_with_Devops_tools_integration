from flask import Flask
from config import Config
from flask_wtf.csrf import CSRFProtect
from app.routes.employee import employee_bp
from app.routes.department import department_bp
from app.routes.home import home_bp
from app.routes.auth import auth_bp
from app.models import db
from flask_migrate import Migrate

migrate = Migrate()
csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    required = ("SECRET_KEY", "SQLALCHEMY_DATABASE_URI", "ADMIN_EMAIL", "ADMIN_PASSWORD_HASH")
    missing = [key for key in required if not app.config.get(key)]
    if missing and not app.config.get("TESTING"):
        raise RuntimeError(
            "Missing required environment configuration: " + ", ".join(missing)
        )

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    app.register_blueprint(home_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(auth_bp)

    # Apply schema changes explicitly with Flask-Migrate/Alembic.
    # Never run create_all() or ad-hoc ALTER TABLE statements at app startup.
    return app
