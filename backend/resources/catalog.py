from flask import make_response, request
from flask_restful import Resource
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from models import db, CatalogService, Subscription, User
from resources.auth_helpers import error_response, jwt_required_restful
from resources.pagination import paginated_response, parse_pagination_args


class CatalogList(Resource):
    """Browse global catalog (JWT). Admin can also create templates."""

    method_decorators = [jwt_required_restful]

    def get(self):
        page, per_page, err = parse_pagination_args()
        if err:
            return err

        q = (request.args.get("q") or request.args.get("search") or "").strip()
        category = (request.args.get("category") or "").strip()
        min_cost = request.args.get("min_cost")
        max_cost = request.args.get("max_cost")

        query = CatalogService.query.order_by(CatalogService.service_name.asc())
        if q:
            like = f"%{q}%"
            query = query.filter(
                or_(
                    CatalogService.service_name.ilike(like),
                    CatalogService.category.ilike(like),
                )
            )
        if category:
            query = query.filter(CatalogService.category == category)
        try:
            if min_cost is not None and min_cost != "":
                query = query.filter(CatalogService.default_cost >= float(min_cost))
            if max_cost is not None and max_cost != "":
                query = query.filter(CatalogService.default_cost <= float(max_cost))
        except ValueError:
            return error_response("min_cost and max_cost must be numbers")

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        items = [s.to_dict() for s in pagination.items]
        return make_response(paginated_response(pagination, items), 200)

    def post(self):
        from resources.auth_helpers import current_user

        user = current_user()
        if not user or not user.is_admin:
            return error_response("Admin access required", 403)

        data = request.get_json() or {}
        service_name = (data.get("service_name") or "").strip()
        category = (data.get("category") or "").strip()
        if not service_name:
            return error_response("service_name is required")
        if not category:
            return error_response("category is required")

        try:
            default_cost = float(data.get("default_cost", 0))
            default_trial_days = int(data.get("default_trial_days", 0))
            if default_cost < 0 or default_trial_days < 0:
                return error_response("costs and trial days must be >= 0")

            service = CatalogService(
                service_name=service_name,
                category=category,
                default_cost=default_cost,
                default_trial_days=default_trial_days,
            )
            db.session.add(service)
            db.session.commit()
        except (TypeError, ValueError):
            db.session.rollback()
            return error_response("Invalid default_cost or default_trial_days")
        except IntegrityError:
            db.session.rollback()
            return error_response("Service name must be unique", 409)

        return make_response(service.to_dict(), 201)


class CatalogDetail(Resource):
    method_decorators = [jwt_required_restful]

    def get(self, id):
        service = db.session.get(CatalogService, id)
        if not service:
            return error_response("Catalog service not found", 404)
        return make_response(service.to_dict(), 200)

    def patch(self, id):
        from resources.auth_helpers import current_user

        user = current_user()
        if not user or not user.is_admin:
            return error_response("Admin access required", 403)

        service = db.session.get(CatalogService, id)
        if not service:
            return error_response("Catalog service not found", 404)

        data = request.get_json() or {}
        try:
            if "service_name" in data:
                name = (data["service_name"] or "").strip()
                if not name:
                    return error_response("service_name is required")
                service.service_name = name
            if "category" in data:
                category = (data["category"] or "").strip()
                if not category:
                    return error_response("category is required")
                service.category = category
            if "default_cost" in data:
                cost = float(data["default_cost"])
                if cost < 0:
                    return error_response("default_cost must be >= 0")
                service.default_cost = cost
            if "default_trial_days" in data:
                days = int(data["default_trial_days"])
                if days < 0:
                    return error_response("default_trial_days must be >= 0")
                service.default_trial_days = days
            db.session.commit()
        except (TypeError, ValueError):
            db.session.rollback()
            return error_response("Invalid field values")
        except IntegrityError:
            db.session.rollback()
            return error_response("Service name must be unique", 409)

        return make_response(service.to_dict(), 200)

    def delete(self, id):
        from resources.auth_helpers import current_user

        user = current_user()
        if not user or not user.is_admin:
            return error_response("Admin access required", 403)

        service = db.session.get(CatalogService, id)
        if not service:
            return error_response("Catalog service not found", 404)
        db.session.delete(service)
        db.session.commit()
        return make_response("", 204)


class CatalogSubscribers(Resource):
    """
    Deep query: join Subscription + User (+ Profile) for a catalog service.
    Who is tracking this template (many:many side).
    """

    method_decorators = [jwt_required_restful]

    def get(self, id):
        service = db.session.get(CatalogService, id)
        if not service:
            return error_response("Catalog service not found", 404)

        page, per_page, err = parse_pagination_args()
        if err:
            return err

        query = (
            db.session.query(Subscription)
            .options(
                joinedload(Subscription.user).joinedload(User.profile),
            )
            .filter(Subscription.catalog_service_id == id)
            .order_by(Subscription.enrolled_at.desc())
        )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        items = []
        for sub in pagination.items:
            row = {
                "subscription_id": sub.id,
                "cost": sub.cost,
                "is_trial": sub.is_trial,
                "enrolled_at": sub.enrolled_at.isoformat() if sub.enrolled_at else None,
                "user": sub.user.to_dict() if sub.user else None,
            }
            if sub.user and sub.user.profile:
                row["profile"] = sub.user.profile.to_dict()
            items.append(row)

        return make_response(paginated_response(pagination, items), 200)
