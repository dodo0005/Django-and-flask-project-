from flask import Flask
from config import Config
from extensions import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from routes.stories import stories_bp
    from routes.pages import pages_bp
    from routes.choices import choices_bp

    app.register_blueprint(stories_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(choices_bp)

    return app

app = create_app()
