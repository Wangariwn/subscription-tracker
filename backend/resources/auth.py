from flask import make_response, request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from models import db, User, Profile
from resources.auth_helpers import current_user, error_response, jwt_required_restful


class Register(Resource):
    def post(self):
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        display_name = (data.get("display_name") or username).strip()

        if not username or len(username) < 3:
            return error_response("Username must be at least 3 characters")
        if not email or "@" not in email:
            return error_response("A valid email is required")

        try:
            user = User(username=username, email=email, role="user")
            user.set_password(password)
            user.profile = Profile(
                display_name=display_name or username,
                preferred_currency=data.get("preferred_currency") or "USD",
                timezone=data.get("timezone") or "UTC",
            )
            db.session.add(user)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return error_response(str(err))
        except IntegrityError:
            db.session.rollback()
            return error_response("Username or email already exists")

        return make_response(user.to_dict(), 201)


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return error_response("Username and password are required")

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return error_response("Invalid username or password", 401)

        token = create_access_token(identity=str(user.id))
        return make_response(
            {
                "access_token": token,
                "user": user.to_dict(),
            },
            200,
        )


class Me(Resource):
    method_decorators = [jwt_required_restful]

    def get(self):
        user = current_user()
        if not user:
            return error_response("User not found", 404)
        payload = user.to_dict()
        if user.profile:
            payload["profile"] = user.profile.to_dict()
        return make_response(payload, 200)
