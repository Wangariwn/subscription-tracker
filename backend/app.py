from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api

from config import Config
from models import db
from resources import register_resources

migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.compact = False

    raw_origin = app.config.get("FRONTEND_ORIGIN", "*")
    if raw_origin == "*":
        CORS(app)
    else:
        origins = [part.strip() for part in raw_origin.split(",") if part.strip()]
        # Always allow this project's Vercel production + preview URLs
        origins.extend(
            [
                "https://renewly-ivory.vercel.app",
                r"https://renewly-.*\.vercel\.app",
                "http://127.0.0.1:5173",
                "http://localhost:5173",
            ]
        )
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for item in origins:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        CORS(app, origins=unique, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    api = Api(app)
    register_resources(api)

    @app.get("/")
    def health():
        """Render / uptime health check — not the React UI."""
        return jsonify(
            {
                "status": "ok",
                "service": "renewly-api",
                "message": "API is running. Use the Vercel frontend URL in the browser.",
            }
        )

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({"errors": [reason]}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"errors": [reason]}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"errors": ["Token has expired"]}), 401

    return app


app = create_app()


if __name__ == "__main__":
    app.run(port=5555, debug=True)
