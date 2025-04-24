# app/__init__.py

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import static

from app.routes import (
    auth_bp, register_bp, catalogue_bp,
    tables_bp, admin_bp
)

def create_app():
    load_dotenv()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(BASE_DIR, "..", "static")

    app = Flask(__name__, static_folder=static_path, static_url_path="/static")

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')

    # Init JWT + CORS
    jwt = JWTManager(app)
    CORS(app)

    # Register all Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(catalogue_bp)
    app.register_blueprint(tables_bp)
    app.register_blueprint(admin_bp)

    return app
