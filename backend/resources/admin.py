from flask import make_response, request
from flask_restful import Resource
from sqlalchemy.orm import joinedload

from models import CatalogService, Subscription, User
from resources.auth_helpers import admin_required
from resources.pagination import paginated_response, parse_pagination_args
from resources.subscriptions import apply_subscription_filters, serialize_subscription


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


class AdminSubscriptions(Resource):
    """Admin-only: list every subscription across all users."""

    method_decorators = [admin_required]

    def get(self):
        page, per_page, err = parse_pagination_args()
        if err:
            return err

        query = (
            Subscription.query.options(
                joinedload(Subscription.catalog_service),
                joinedload(Subscription.user),
            )
            .join(CatalogService)
            .join(User)
            .order_by(Subscription.renewal_date.asc(), Subscription.id.asc())
        )

        query, filter_err = apply_subscription_filters(
            query,
            q_columns=(
                CatalogService.service_name,
                CatalogService.category,
                User.username,
                User.email,
            ),
        )
        if filter_err:
            return filter_err

        username = (request.args.get("username") or "").strip()
        if username:
            query = query.filter(User.username.ilike(f"%{username}%"))

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [
            serialize_subscription(s, include_user=True) for s in pagination.items
        ]
        return make_response(paginated_response(pagination, items), 200)
