import os
from datetime import date, timedelta
from functools import wraps

from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, User, CatalogService, Subscription
from schemas import (
    user_schema,
    register_schema,
    login_schema,
    catalog_service_schema,
    catalog_services_schema,
    subscription_schema,
    subscriptions_schema,
)

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


def error_response(message, status=400):
    if isinstance(message, str):
        message = [message]
    return make_response({"errors": message}, status)


def current_user():
    identity = get_jwt_identity()
    if identity is None:
        return None
    return db.session.get(User, int(identity))


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or not user.is_admin:
            return error_response("Admin access required", 403)
        return fn(*args, **kwargs)

    return wrapper


# ---------- Auth ----------


@app.route("/auth/register", methods=["POST"])
def register():
    """Register a new user (role defaults to user)."""
    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        data = register_schema.load(json_data)
        user = User(
            username=data["username"],
            email=data["email"],
            role="user",
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return make_response(user_schema.dump(user), 201)
    except ValidationError as err:
        return error_response(err.messages)
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err))
    except IntegrityError:
        db.session.rollback()
        return error_response("Username or email already exists")


@app.route("/auth/login", methods=["POST"])
def login():
    """Login and receive a JWT access token."""
    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        data = login_schema.load(json_data)
    except ValidationError as err:
        return error_response(err.messages)

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return error_response("Invalid username or password", 401)

    token = create_access_token(identity=str(user.id))
    return make_response(
        {
            "access_token": token,
            "user": user_schema.dump(user),
        },
        200,
    )


# ---------- User dashboard & subscriptions ----------


@app.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    """Personal dashboard: active subs, monthly spend, trial alerts."""
    user = current_user()
    today = date.today()
    subscriptions = Subscription.query.filter_by(user_id=user.id).all()

    monthly_spend = sum(sub.cost for sub in subscriptions if not sub.is_trial)
    upcoming = sorted(subscriptions, key=lambda s: s.renewal_date)[:5]
    trial_alerts = [
        sub
        for sub in subscriptions
        if sub.is_trial
        and sub.trial_expiration_date
        and sub.trial_expiration_date <= today + timedelta(days=7)
    ]

    return make_response(
        {
            "user": user_schema.dump(user),
            "total_subscriptions": len(subscriptions),
            "monthly_spend": round(monthly_spend, 2),
            "upcoming_renewals": subscriptions_schema.dump(upcoming),
            "trial_alerts": subscriptions_schema.dump(trial_alerts),
        },
        200,
    )


@app.route("/subscriptions", methods=["GET"])
@jwt_required()
def get_subscriptions():
    """List current user's subscriptions."""
    user = current_user()
    subs = Subscription.query.filter_by(user_id=user.id).all()
    return make_response(subscriptions_schema.dump(subs), 200)


@app.route("/subscriptions/<int:id>", methods=["GET"])
@jwt_required()
def get_subscription(id):
    """Show one of the current user's subscriptions."""
    user = current_user()
    sub = db.session.get(Subscription, id)
    if not sub or sub.user_id != user.id:
        return error_response("Subscription not found", 404)
    return make_response(subscription_schema.dump(sub), 200)


@app.route("/subscriptions", methods=["POST"])
@jwt_required()
def create_subscription():
    """Create a subscription for the current user."""
    user = current_user()
    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        sub = subscription_schema.load(json_data)
        sub.user_id = user.id
        db.session.add(sub)
        db.session.commit()
        return make_response(subscription_schema.dump(sub), 201)
    except ValidationError as err:
        return error_response(err.messages)
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err))
    except IntegrityError:
        db.session.rollback()
        return error_response("Could not create subscription")


@app.route("/subscriptions/<int:id>", methods=["PATCH"])
@jwt_required()
def update_subscription(id):
    """Update one of the current user's subscriptions."""
    user = current_user()
    sub = db.session.get(Subscription, id)
    if not sub or sub.user_id != user.id:
        return error_response("Subscription not found", 404)

    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        updated = subscription_schema.load(json_data, instance=sub, partial=True)
        db.session.commit()
        return make_response(subscription_schema.dump(updated), 200)
    except ValidationError as err:
        return error_response(err.messages)
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err))


@app.route("/subscriptions/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_subscription(id):
    """Delete one of the current user's subscriptions."""
    user = current_user()
    sub = db.session.get(Subscription, id)
    if not sub or sub.user_id != user.id:
        return error_response("Subscription not found", 404)

    db.session.delete(sub)
    db.session.commit()
    return make_response("", 204)


@app.route("/catalog", methods=["GET"])
@jwt_required()
def browse_catalog():
    """Browse global service catalog templates."""
    services = CatalogService.query.order_by(CatalogService.service_name).all()
    return make_response(catalog_services_schema.dump(services), 200)


# ---------- Admin ----------


@app.route("/admin/analytics", methods=["GET"])
@admin_required
def admin_analytics():
    """Platform statistics (admin only)."""
    total_users = User.query.filter_by(role="user").count()
    total_admins = User.query.filter_by(role="admin").count()
    total_subscriptions = Subscription.query.count()
    total_catalog = CatalogService.query.count()
    trial_count = Subscription.query.filter_by(is_trial=True).count()

    return make_response(
        {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_subscriptions": total_subscriptions,
            "active_trials": trial_count,
            "catalog_services": total_catalog,
        },
        200,
    )


@app.route("/admin/catalog", methods=["GET"])
@admin_required
def admin_list_catalog():
    """List catalog templates (admin only)."""
    services = CatalogService.query.order_by(CatalogService.service_name).all()
    return make_response(catalog_services_schema.dump(services), 200)


@app.route("/admin/catalog", methods=["POST"])
@admin_required
def admin_create_catalog():
    """Create a catalog template (admin only)."""
    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        service = catalog_service_schema.load(json_data)
        db.session.add(service)
        db.session.commit()
        return make_response(catalog_service_schema.dump(service), 201)
    except ValidationError as err:
        return error_response(err.messages)
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err))
    except IntegrityError:
        db.session.rollback()
        return error_response("Service name must be unique")


@app.route("/admin/catalog/<int:id>", methods=["PATCH"])
@admin_required
def admin_update_catalog(id):
    """Update a catalog template (admin only)."""
    service = db.session.get(CatalogService, id)
    if not service:
        return error_response("Catalog service not found", 404)

    json_data = request.get_json()
    if not json_data:
        return error_response("Request body must be JSON")

    try:
        updated = catalog_service_schema.load(
            json_data, instance=service, partial=True
        )
        db.session.commit()
        return make_response(catalog_service_schema.dump(updated), 200)
    except ValidationError as err:
        return error_response(err.messages)
    except ValueError as err:
        db.session.rollback()
        return error_response(str(err))
    except IntegrityError:
        db.session.rollback()
        return error_response("Service name must be unique")


@app.route("/admin/catalog/<int:id>", methods=["DELETE"])
@admin_required
def admin_delete_catalog(id):
    """Delete a catalog template (admin only)."""
    service = db.session.get(CatalogService, id)
    if not service:
        return error_response("Catalog service not found", 404)

    db.session.delete(service)
    db.session.commit()
    return make_response("", 204)


@app.route("/", methods=["GET"])
def index():
    return make_response(
        {
            "message": "Subscription & Free Trial Tracker API",
            "docs": "See README.md for endpoints",
        },
        200,
    )


if __name__ == "__main__":
    app.run(port=5555, debug=True)
