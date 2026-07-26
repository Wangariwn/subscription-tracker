from flask import make_response
from flask_restful import Resource

from models import User
from resources.auth_helpers import admin_required


class AdminUsers(Resource):
    """Admin-only: list all users. Regular users get 403."""

    method_decorators = [admin_required]

    def get(self):
        users = User.query.order_by(User.id).all()
        return make_response(
            {
                "users": [u.to_dict() for u in users],
                "total": len(users),
            },
            200,
        )
