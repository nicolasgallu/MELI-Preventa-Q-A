from flask import Flask
from app.mercadolibre.blueprints.pre_sell import preventa_bp
from app.whatsapp.blueprints.human_reply import wpp_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(preventa_bp)
    app.register_blueprint(wpp_bp) 
    return app