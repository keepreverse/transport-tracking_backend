import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.getenv(
        'UPLOAD_FOLDER',
        os.path.join(BASE_DIR, 'uploads')
    )

    MAX_CONTENT_LENGTH = int(
        os.getenv('MAX_CONTENT_LENGTH', 100 * 1024 * 1024)
    )

    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'dev-key-change-in-production'
    )

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }