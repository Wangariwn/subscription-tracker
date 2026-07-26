from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from models import db, User, CatalogService, Subscription, VALID_ROLES


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False
        sqla_session = db.session
        exclude = ("password_hash",)

    id = fields.Integer(dump_only=True)
    username = fields.String(dump_only=True)
    email = fields.Email(dump_only=True)
    role = fields.String(dump_only=True, validate=validate.OneOf(VALID_ROLES))


class RegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6))


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)


class CatalogServiceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CatalogService
        load_instance = True
        sqla_session = db.session

    id = fields.Integer(dump_only=True)
    service_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    default_cost = fields.Float(required=True, validate=validate.Range(min=0))
    category = fields.String(required=True, validate=validate.Length(min=1, max=80))
    default_trial_days = fields.Integer(required=True, validate=validate.Range(min=0))


class SubscriptionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Subscription
        load_instance = True
        sqla_session = db.session
        include_fk = True

    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    service_name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    cost = fields.Float(required=True, validate=validate.Range(min=0))
    renewal_date = fields.Date(required=True)
    is_trial = fields.Boolean(load_default=False)
    trial_expiration_date = fields.Date(allow_none=True, load_default=None)

    @validates_schema
    def validate_trial_fields(self, data, **kwargs):
        is_trial = data.get("is_trial", False)
        trial_expiration_date = data.get("trial_expiration_date")
        if is_trial and trial_expiration_date is None:
            raise ValidationError(
                "trial_expiration_date is required when is_trial is true",
                field_name="trial_expiration_date",
            )


user_schema = UserSchema()
users_schema = UserSchema(many=True)
register_schema = RegisterSchema()
login_schema = LoginSchema()
catalog_service_schema = CatalogServiceSchema()
catalog_services_schema = CatalogServiceSchema(many=True)
subscription_schema = SubscriptionSchema()
subscriptions_schema = SubscriptionSchema(many=True)
