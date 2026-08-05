import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


def _database_uri():
    uri = os.environ.get("DATABASE_URI", "sqlite:///app.db")
    # Render/Heroku style URLs
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    return uri


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-only-change-me-secret-key-32chars!!",
    )
    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET",
        "dev-only-change-me-jwt-secret-key-32chars!!",
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "15"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_DAYS", "30"))
    )
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")
    FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "*")


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)
    CLOUDINARY_CLOUD_NAME = None
    CLOUDINARY_API_KEY = None
    CLOUDINARY_API_SECRET = None
