from datetime import date, timedelta

from flask import make_response
from flask_restful import Resource
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from models import CatalogService, Subscription, User
from resources.auth_helpers import (
    admin_required,
    current_user,
    jwt_required_restful,
)
from resources.subscriptions import serialize_subscription


class Dashboard(Resource):
    """
    Deep query #1: personal dashboard with join/eager load, spend aggregate,
    and relationship-filtered trial alerts.
    """

    method_decorators = [jwt_required_restful]

    def get(self):
        user = current_user()
        today = date.today()

        subscriptions = (
            Subscription.query.options(joinedload(Subscription.catalog_service))
            .filter_by(user_id=user.id)
            .order_by(Subscription.renewal_date.asc())
            .all()
        )

        monthly_spend = (
            Subscription.query.with_entities(func.coalesce(func.sum(Subscription.cost), 0.0))
            .filter(
                Subscription.user_id == user.id,
                Subscription.is_trial.is_(False),
            )
            .scalar()
        )

        trial_alerts = [
            serialize_subscription(sub)
            for sub in subscriptions
            if sub.is_trial
            and sub.trial_expiration_date
            and sub.trial_expiration_date <= today + timedelta(days=7)
        ]

        upcoming = [serialize_subscription(sub) for sub in subscriptions[:5]]

        payload = {
            "user": user.to_dict(),
            "total_subscriptions": len(subscriptions),
            "monthly_spend": round(float(monthly_spend), 2),
            "upcoming_renewals": upcoming,
            "trial_alerts": trial_alerts,
        }
        if user.profile:
            payload["profile"] = user.profile.to_dict()
        return make_response(payload, 200)


class AdminAnalytics(Resource):
    """
    Deep query #2: aggregates with group_by / having across joined tables.
    """

    method_decorators = [admin_required]

    def get(self):
        total_users = User.query.filter_by(role="user").count()
        total_admins = User.query.filter_by(role="admin").count()
        total_subscriptions = Subscription.query.count()
        active_trials = Subscription.query.filter_by(is_trial=True).count()
        catalog_services = CatalogService.query.count()

        spend_total = (
            Subscription.query.with_entities(
                func.coalesce(func.sum(Subscription.cost), 0.0)
            )
            .filter(Subscription.is_trial.is_(False))
            .scalar()
        )

        # Join Subscription ↔ CatalogService; group by category; having count >= 1
        by_category = (
            db_session_query_category_stats()
        )

        popular_services = (
            Subscription.query.join(CatalogService)
            .with_entities(
                CatalogService.service_name,
                CatalogService.category,
                func.count(Subscription.id).label("subscribers"),
                func.coalesce(func.sum(Subscription.cost), 0.0).label("revenue"),
            )
            .group_by(CatalogService.id, CatalogService.service_name, CatalogService.category)
            .having(func.count(Subscription.id) >= 1)
            .order_by(func.count(Subscription.id).desc())
            .limit(10)
            .all()
        )

        # Users who have any trial subscription (.any())
        users_on_trial = (
            User.query.filter(User.subscriptions.any(Subscription.is_trial.is_(True)))
            .count()
        )

        return make_response(
            {
                "total_users": total_users,
                "total_admins": total_admins,
                "total_subscriptions": total_subscriptions,
                "active_trials": active_trials,
                "users_on_trial": users_on_trial,
                "catalog_services": catalog_services,
                "platform_monthly_spend": round(float(spend_total), 2),
                "subscriptions_by_category": by_category,
                "popular_services": [
                    {
                        "service_name": row.service_name,
                        "category": row.category,
                        "subscribers": row.subscribers,
                        "revenue": round(float(row.revenue), 2),
                    }
                    for row in popular_services
                ],
            },
            200,
        )


def db_session_query_category_stats():
    rows = (
        Subscription.query.join(CatalogService)
        .with_entities(
            CatalogService.category,
            func.count(Subscription.id).label("subscription_count"),
            func.coalesce(func.sum(Subscription.cost), 0.0).label("total_cost"),
        )
        .group_by(CatalogService.category)
        .having(func.count(Subscription.id) >= 1)
        .order_by(func.count(Subscription.id).desc())
        .all()
    )
    return [
        {
            "category": row.category,
            "subscription_count": row.subscription_count,
            "total_cost": round(float(row.total_cost), 2),
        }
        for row in rows
    ]
