from flask import Flask
from flask_cors import CORS

from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    from .services import db_service
    db_service.init_app(app)

    from .blueprints import auth
    app.register_blueprint(auth.bp)

    from .blueprints import news
    app.register_blueprint(news.bp)

    from .blueprints import reports
    app.register_blueprint(reports.bp)

    return app