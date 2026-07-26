#!/usr/bin/env python3

from datetime import date, timedelta

from app import app
from models import db, User, CatalogService, Subscription

with app.app_context():
    print("Clearing tables...")
    Subscription.query.delete()
    CatalogService.query.delete()
    User.query.delete()
    db.session.commit()

    admin = User(username="admin", email="admin@example.com", role="admin")
    admin.set_password("admin123")

    demo = User(username="demo", email="demo@example.com", role="user")
    demo.set_password("demo123")

    other = User(username="alex", email="alex@example.com", role="user")
    other.set_password("alex123")

    db.session.add_all([admin, demo, other])
    db.session.commit()

    catalog = [
        CatalogService(
            service_name="Netflix",
            default_cost=15.49,
            category="Streaming",
            default_trial_days=30,
        ),
        CatalogService(
            service_name="Spotify",
            default_cost=10.99,
            category="Music",
            default_trial_days=30,
        ),
        CatalogService(
            service_name="Adobe Creative Cloud",
            default_cost=54.99,
            category="Productivity",
            default_trial_days=7,
        ),
        CatalogService(
            service_name="Disney+",
            default_cost=9.99,
            category="Streaming",
            default_trial_days=0,
        ),
        CatalogService(
            service_name="ChatGPT Plus",
            default_cost=20.00,
            category="AI",
            default_trial_days=0,
        ),
    ]
    db.session.add_all(catalog)
    db.session.commit()

    today = date.today()
    subscriptions = [
        Subscription(
            user_id=demo.id,
            service_name="Netflix",
            cost=15.49,
            renewal_date=today + timedelta(days=12),
            is_trial=False,
            trial_expiration_date=None,
        ),
        Subscription(
            user_id=demo.id,
            service_name="Spotify",
            cost=0.0,
            renewal_date=today + timedelta(days=5),
            is_trial=True,
            trial_expiration_date=today + timedelta(days=5),
        ),
        Subscription(
            user_id=demo.id,
            service_name="ChatGPT Plus",
            cost=20.00,
            renewal_date=today + timedelta(days=20),
            is_trial=False,
            trial_expiration_date=None,
        ),
        Subscription(
            user_id=other.id,
            service_name="Disney+",
            cost=9.99,
            renewal_date=today + timedelta(days=8),
            is_trial=False,
            trial_expiration_date=None,
        ),
    ]
    db.session.add_all(subscriptions)
    db.session.commit()

    print(
        f"Seeded {User.query.count()} users, "
        f"{CatalogService.query.count()} catalog services, "
        f"{Subscription.query.count()} subscriptions."
    )
    print("Accounts -> admin/admin123 (admin), demo/demo123 (user)")
