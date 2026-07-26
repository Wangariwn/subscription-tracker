from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

VALID_ROLES = ("user", "admin")


class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    serialize_rules = ("-password_hash", "-subscriptions.user")

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    subscriptions = db.relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class CatalogService(db.Model, SerializerMixin):
    __tablename__ = "catalog_services"

    serialize_rules = ()

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(120), nullable=False, unique=True)
    default_cost = db.Column(db.Float, nullable=False, default=0.0)
    category = db.Column(db.String(80), nullable=False)
    default_trial_days = db.Column(db.Integer, nullable=False, default=0)


class Subscription(db.Model, SerializerMixin):
    __tablename__ = "subscriptions"

    serialize_rules = ("-user.subscriptions",)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_name = db.Column(db.String(120), nullable=False)
    cost = db.Column(db.Float, nullable=False, default=0.0)
    renewal_date = db.Column(db.Date, nullable=False)
    is_trial = db.Column(db.Boolean, nullable=False, default=False)
    trial_expiration_date = db.Column(db.Date, nullable=True)

    user = db.relationship("User", back_populates="subscriptions")
