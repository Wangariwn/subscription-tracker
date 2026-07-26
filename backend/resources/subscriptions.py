from datetime import date, datetime

from flask import make_response, request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from models import db, CatalogService, Subscription
from resources.auth_helpers import current_user, error_response, jwt_required_restful
from resources.pagination import paginated_response, parse_pagination_args


def parse_date(value, field_name):
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        raise ValueError(f"{field_name} must be an ISO date (YYYY-MM-DD)")


def serialize_subscription(sub):
    data = sub.to_dict()
    if sub.catalog_service:
        data["catalog_service"] = sub.catalog_service.to_dict()
    return data


class SubscriptionList(Resource):
    """Paginated CRUD list/create for the current user's subscriptions."""

    method_decorators = [jwt_required_restful]

    def get(self):
        """
        Deep query: filter across relationships (category), order_by renewal,
        eager-load catalog_service to avoid N+1.
        """
        user = current_user()
        page, per_page, err = parse_pagination_args()
        if err:
            return err

        category = (request.args.get("category") or "").strip()
        is_trial = request.args.get("is_trial")

        query = (
            Subscription.query.options(joinedload(Subscription.catalog_service))
            .filter_by(user_id=user.id)
            .order_by(Subscription.renewal_date.asc())
        )

        if category:
            # Filter across User → Subscription → CatalogService relationship
            query = query.filter(
                Subscription.catalog_service.has(CatalogService.category == category)
            )

        if is_trial is not None and is_trial != "":
            flag = str(is_trial).lower() in ("1", "true", "yes")
            query = query.filter_by(is_trial=flag)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [serialize_subscription(s) for s in pagination.items]
        return make_response(paginated_response(pagination, items), 200)

    def post(self):
        user = current_user()
        data = request.get_json() or {}

        catalog_service_id = data.get("catalog_service_id")
        if not catalog_service_id:
            return error_response("catalog_service_id is required")

        service = db.session.get(CatalogService, catalog_service_id)
        if not service:
            return error_response("Catalog service not found", 404)

        try:
            is_trial = bool(data.get("is_trial", False))
            trial_expiration_date = parse_date(
                data.get("trial_expiration_date"), "trial_expiration_date"
            )
            if is_trial and trial_expiration_date is None:
                return error_response(
                    "trial_expiration_date is required when is_trial is true"
                )

            cost = data.get("cost", service.default_cost)
            if cost is None or float(cost) < 0:
                return error_response("cost must be >= 0")

            renewal_date = parse_date(data.get("renewal_date"), "renewal_date")
            if renewal_date is None:
                return error_response("renewal_date is required")

            enrolled_at = parse_date(data.get("enrolled_at"), "enrolled_at") or date.today()

            sub = Subscription(
                user_id=user.id,
                catalog_service_id=service.id,
                cost=float(cost),
                renewal_date=renewal_date,
                is_trial=is_trial,
                trial_expiration_date=trial_expiration_date,
                enrolled_at=enrolled_at,
            )
            db.session.add(sub)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return error_response(str(err))
        except IntegrityError:
            db.session.rollback()
            return error_response(
                "You already track this catalog service",
                409,
            )

        sub = (
            Subscription.query.options(joinedload(Subscription.catalog_service))
            .filter_by(id=sub.id)
            .one()
        )
        return make_response(serialize_subscription(sub), 201)


class SubscriptionDetail(Resource):
    method_decorators = [jwt_required_restful]

    def _owned(self, sub_id):
        user = current_user()
        return (
            Subscription.query.options(joinedload(Subscription.catalog_service))
            .filter_by(id=sub_id, user_id=user.id)
            .first()
        )

    def get(self, id):
        sub = self._owned(id)
        if not sub:
            return error_response("Subscription not found", 404)
        return make_response(serialize_subscription(sub), 200)

    def patch(self, id):
        sub = self._owned(id)
        if not sub:
            return error_response("Subscription not found", 404)

        data = request.get_json() or {}
        try:
            if "cost" in data:
                cost = float(data["cost"])
                if cost < 0:
                    return error_response("cost must be >= 0")
                sub.cost = cost
            if "renewal_date" in data:
                renewal_date = parse_date(data["renewal_date"], "renewal_date")
                if renewal_date is None:
                    return error_response("renewal_date is required")
                sub.renewal_date = renewal_date
            if "is_trial" in data:
                sub.is_trial = bool(data["is_trial"])
            if "trial_expiration_date" in data:
                sub.trial_expiration_date = parse_date(
                    data["trial_expiration_date"], "trial_expiration_date"
                )
            if "enrolled_at" in data:
                enrolled_at = parse_date(data["enrolled_at"], "enrolled_at")
                if enrolled_at is None:
                    return error_response("enrolled_at is required")
                sub.enrolled_at = enrolled_at
            if "catalog_service_id" in data:
                service = db.session.get(CatalogService, data["catalog_service_id"])
                if not service:
                    return error_response("Catalog service not found", 404)
                sub.catalog_service_id = service.id

            if sub.is_trial and sub.trial_expiration_date is None:
                return error_response(
                    "trial_expiration_date is required when is_trial is true"
                )

            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return error_response(str(err))
        except IntegrityError:
            db.session.rollback()
            return error_response(
                "You already track this catalog service",
                409,
            )

        return make_response(serialize_subscription(sub), 200)

    def delete(self, id):
        sub = self._owned(id)
        if not sub:
            return error_response("Subscription not found", 404)
        db.session.delete(sub)
        db.session.commit()
        return make_response("", 204)
