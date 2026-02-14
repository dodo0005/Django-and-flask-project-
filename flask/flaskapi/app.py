from flask import Flask
from config import Config
from extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from models import Story, Page, Choice

    from routes.stories import stories_bp
    from routes.pages import pages_bp

    # Note: choice routes live inside pages_bp (/pages/<id>/choices)

    app.register_blueprint(stories_bp)
    app.register_blueprint(pages_bp)

    return app


app = create_app()
