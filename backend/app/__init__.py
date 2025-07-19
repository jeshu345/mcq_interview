from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError

from .config import Config
from .models import db
from .routes.admin_routes import admin_bp
from .routes.candidate_routes import candidate_bp  # Import your candidate routes
from .views.admin_views import load_mcqs_from_json  # Import your CLI function here

from flask_migrate import Migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    from flask_cors import CORS

# Inside create_app()
    CORS(app, supports_credentials=True, origins="*")  # Allow all origins


    migrate = Migrate(app, db)

    jwt = JWTManager(app)

    @app.cli.command("load_mcqs")
    def load_mcqs():
        load_mcqs_from_json('python_mcqs.json', batch_id=1, admin_id=1)

    @app.errorhandler(NoAuthorizationError)
    def handle_missing_token(e):
        return jsonify({'message': 'Token is missing.'}), 401

    @app.errorhandler(JWTDecodeError)
    def handle_invalid_token(e):
        return jsonify({'message': 'Token is invalid.'}), 401

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(candidate_bp, url_prefix='/candidate')  
    

    with app.app_context():
        db.create_all()

    return app
