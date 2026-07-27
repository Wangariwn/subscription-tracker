from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

VALID_ROLES = ("user", "admin")


class User(db.Model, SerializerMixin):
    """Account identity. Has one Profile (1:1) and many Subscriptions (1:many)."""

    __tablename__ = "users"

    serialize_rules = (
        "-password_hash",
        "-profile.user",
        "-subscriptions.user",
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")

    # 1:1 — User has exactly one Profile
    profile = db.relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # 1:many — User has many Subscriptions (association rows)
    subscriptions = db.relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # many:many via association object — services this user tracks
    catalog_services = association_proxy("subscriptions", "catalog_service")

    def set_password(self, password):
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


class Profile(db.Model, SerializerMixin):
    """1:1 extension of User (preferences / display info)."""

    __tablename__ = "profiles"

    serialize_rules = ("-user.profile", "-user.subscriptions")

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    display_name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.String(255), nullable=True)
    preferred_currency = db.Column(db.String(3), nullable=False, default="USD")
    timezone = db.Column(db.String(64), nullable=False, default="UTC")
    avatar_url = db.Column(db.String(512), nullable=True)

    user = db.relationship("User", back_populates="profile")


class CatalogService(db.Model, SerializerMixin):
    """Global service template. Many users track each service via Subscription."""

    __tablename__ = "catalog_services"

    serialize_rules = ("-subscriptions.catalog_service",)

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(120), nullable=False, unique=True)
    default_cost = db.Column(db.Float, nullable=False, default=0.0)
    category = db.Column(db.String(80), nullable=False)
    default_trial_days = db.Column(db.Integer, nullable=False, default=0)

    subscriptions = db.relationship(
        "Subscription",
        back_populates="catalog_service",
        cascade="all, delete-orphan",
    )

    # many:many via association object — users tracking this service
    users = association_proxy("subscriptions", "user")


class Subscription(db.Model, SerializerMixin):
    """
    Association object for User ↔ CatalogService (many:many) with extra data:
    cost, renewal_date, trial flags, and enrolled_at.
    Also serves as the 1:many child of User.
    """

    __tablename__ = "subscriptions"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "catalog_service_id",
            name="uq_user_catalog_service",
        ),
    )

    serialize_rules = (
        "-user.subscriptions",
        "-user.profile",
        "-catalog_service.subscriptions",
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    catalog_service_id = db.Column(
        db.Integer,
        db.ForeignKey("catalog_services.id", ondelete="CASCADE"),
        nullable=False,
    )
    cost = db.Column(db.Float, nullable=False, default=0.0)
    renewal_date = db.Column(db.Date, nullable=False)
    is_trial = db.Column(db.Boolean, nullable=False, default=False)
    trial_expiration_date = db.Column(db.Date, nullable=True)
    enrolled_at = db.Column(db.Date, nullable=False, default=date.today)

    user = db.relationship("User", back_populates="subscriptions")
    catalog_service = db.relationship(
        "CatalogService",
        back_populates="subscriptions",
    )
