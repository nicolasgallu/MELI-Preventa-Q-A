from flask import Flask
from app.blueprints.blueprint_preventa import preventa_bp
from app.blueprints.blueprint_wpp import wpp_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(preventa_bp)
    app.register_blueprint(wpp_bp) 
    return app