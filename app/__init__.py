from flask import Flask
from app.blueprints.webhook import webhook_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(webhook_blueprint, url_prefix="/webhook")
    return app