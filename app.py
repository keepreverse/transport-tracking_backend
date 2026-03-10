import os
from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes.tracks import tracks_bp
from routes.files import files_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)  # разрешаем запросы с фронтенда

    db.init_app(app)

    # Создаём папку для загрузок, если её нет
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Регистрируем blueprints
    app.register_blueprint(tracks_bp, url_prefix='/api/tracks')
    app.register_blueprint(files_bp, url_prefix='/api/files')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)