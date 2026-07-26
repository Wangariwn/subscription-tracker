import os

from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from models import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY",
    "dev-only-change-me",
)
app.json.compact = False

migrate = Migrate(app, db)
jwt = JWTManager(app)

db.init_app(app)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
