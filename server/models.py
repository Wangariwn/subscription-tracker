from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

VALID_ROLES = ("user", "admin")


class User(db.Model, SerializerMixin):
    __tablename__ = "users"
    __table_args__ = (
        db.CheckConstraint(
            "role IN ('user', 'admin')",
            name="ck_users_valid_role",
        ),
    )

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

    def set_password(self, password):
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @validates("username")
    def validate_username(self, key, username):
        if not username or not str(username).strip():
            raise ValueError("Username is required")
        cleaned = str(username).strip()
        if len(cleaned) < 3:
            raise ValueError("Username must be at least 3 characters")
        return cleaned

    @validates("email")
    def validate_email(self, key, email):
        if not email or "@" not in str(email):
            raise ValueError("A valid email is required")
        return str(email).strip().lower()

    @validates("role")
    def validate_role(self, key, role):
        if role not in VALID_ROLES:
            raise ValueError(f"Role must be one of: {', '.join(VALID_ROLES)}")
        return role

    def __repr__(self):
        return f"<User {self.id}: {self.username} ({self.role})>"


class CatalogService(db.Model, SerializerMixin):
    __tablename__ = "catalog_services"
    __table_args__ = (
        db.CheckConstraint(
            "default_cost >= 0",
            name="ck_catalog_default_cost_nonneg",
        ),
        db.CheckConstraint(
            "default_trial_days >= 0",
            name="ck_catalog_trial_days_nonneg",
        ),
    )

    serialize_rules = ()

    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(120), nullable=False, unique=True)
    default_cost = db.Column(db.Float, nullable=False, default=0.0)
    category = db.Column(db.String(80), nullable=False)
    default_trial_days = db.Column(db.Integer, nullable=False, default=0)

    @validates("service_name")
    def validate_service_name(self, key, service_name):
        if not service_name or not str(service_name).strip():
            raise ValueError("Service name is required")
        return str(service_name).strip()

    @validates("default_cost")
    def validate_default_cost(self, key, default_cost):
        if default_cost is None or default_cost < 0:
            raise ValueError("default_cost must be greater than or equal to 0")
        return default_cost

    @validates("category")
    def validate_category(self, key, category):
        if not category or not str(category).strip():
            raise ValueError("Category is required")
        return str(category).strip()

    @validates("default_trial_days")
    def validate_default_trial_days(self, key, default_trial_days):
        if default_trial_days is None or default_trial_days < 0:
            raise ValueError("default_trial_days must be >= 0")
        return default_trial_days

    def __repr__(self):
        return f"<CatalogService {self.id}: {self.service_name}>"


class Subscription(db.Model, SerializerMixin):
    __tablename__ = "subscriptions"
    __table_args__ = (
        db.CheckConstraint("cost >= 0", name="ck_subscriptions_cost_nonneg"),
    )

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

    @validates("service_name")
    def validate_service_name(self, key, service_name):
        if not service_name or not str(service_name).strip():
            raise ValueError("Service name is required")
        return str(service_name).strip()

    @validates("cost")
    def validate_cost(self, key, cost):
        if cost is None or cost < 0:
            raise ValueError("cost must be greater than or equal to 0")
        return cost

    @validates("renewal_date")
    def validate_renewal_date(self, key, renewal_date):
        if renewal_date is None:
            raise ValueError("renewal_date is required")
        return renewal_date

    def __repr__(self):
        return f"<Subscription {self.id}: {self.service_name} user={self.user_id}>"
