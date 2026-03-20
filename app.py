import os
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from models import db
from routes.tracks import tracks_bp
from routes.files import files_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=["https://tracker.harucase.synology.me", "https://api.tracker.harucase.synology.me"])
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    db.init_app(app)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.register_blueprint(tracks_bp, url_prefix='/tracks')
    app.register_blueprint(files_bp, url_prefix='/files')
    with app.app_context():
        db.create_all()
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5051)