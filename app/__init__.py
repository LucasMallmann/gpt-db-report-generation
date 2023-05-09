from flask import Flask
from app.views import main_blueprint
from app.text_to_sql_controller import text_to_sql_bp


def create_app(config_file='config.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(text_to_sql_bp)

    return app
