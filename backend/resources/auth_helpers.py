from functools import wraps

from flask import make_response
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException

from models import db, User


def error_response(message, status=400):
    if isinstance(message, str):
        message = [message]
    return make_response({"errors": message}, status)


def current_user():
    identity = get_jwt_identity()
    if identity is None:
        return None
    return db.session.get(User, int(identity))


def jwt_required_restful(fn):
    """Like @jwt_required, but returns JSON 401 (Flask-RESTful-safe)."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except JWTExtendedException as err:
            return error_response(str(err), 401)
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    """Require a valid JWT and admin role."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except JWTExtendedException as err:
            return error_response(str(err), 401)
        user = current_user()
        if not user or not user.is_admin:
            return error_response("Admin access required", 403)
        return fn(*args, **kwargs)

    return wrapper
