#!/usr/bin/env python3
"""Seed the database with realistic data that exercises every relationship."""

from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from app import app
from models import db, User, Profile, CatalogService, Subscription

TODAY = date.today()


def clear_tables():
    print("Clearing tables...")
    Subscription.query.delete()
    Profile.query.delete()
    CatalogService.query.delete()
    User.query.delete()
    db.session.commit()


def seed_users():
    """Users + 1:1 Profiles."""
    users_data = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "role": "admin",
            "profile": {
                "display_name": "Site Admin",
                "bio": "Manages the global service catalog.",
                "preferred_currency": "USD",
                "timezone": "America/New_York",
            },
        },
        {
            "username": "demo",
            "email": "demo@example.com",
            "password": "demo123",
            "role": "user",
            "profile": {
                "display_name": "Demo User",
                "bio": "Tracks streaming and AI tools.",
                "preferred_currency": "USD",
                "timezone": "Africa/Nairobi",
            },
        },
        {
            "username": "alex",
            "email": "alex@example.com",
            "password": "alex123",
            "role": "user",
            "profile": {
                "display_name": "Alex Rivera",
                "bio": "Music and productivity subscriptions.",
                "preferred_currency": "EUR",
                "timezone": "Europe/Berlin",
            },
        },
        {
            "username": "sam",
            "email": "sam@example.com",
            "password": "sam1234",
            "role": "user",
            "profile": {
                "display_name": "Sam Okello",
                "bio": "On a free trial binge.",
                "preferred_currency": "KES",
                "timezone": "Africa/Nairobi",
            },
        },
    ]

    users = []
    for item in users_data:
        profile_data = item.pop("profile")
        password = item.pop("password")
        user = User(
            username=item["username"],
            email=item["email"],
            role=item["role"],
            password_hash=generate_password_hash(password),
        )
        user.profile = Profile(**profile_data)
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    return {u.username: u for u in users}


def seed_catalog():
    """Global CatalogService templates."""
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
        CatalogService(
            service_name="Notion",
            default_cost=10.00,
            category="Productivity",
            default_trial_days=14,
        ),
    ]
    db.session.add_all(catalog)
    db.session.commit()
    return {c.service_name: c for c in catalog}


def seed_subscriptions(users, catalog):
    """
    Association rows for User ↔ CatalogService (many:many) with extra data.
    Also creates 1:many Subscriptions per user.
    """
    rows = [
        # demo: 3 services (1:many from demo)
        Subscription(
            user_id=users["demo"].id,
            catalog_service_id=catalog["Netflix"].id,
            cost=15.49,
            renewal_date=TODAY + timedelta(days=12),
            is_trial=False,
            trial_expiration_date=None,
            enrolled_at=TODAY - timedelta(days=80),
        ),
        Subscription(
            user_id=users["demo"].id,
            catalog_service_id=catalog["Spotify"].id,
            cost=0.0,
            renewal_date=TODAY + timedelta(days=5),
            is_trial=True,
            trial_expiration_date=TODAY + timedelta(days=5),
            enrolled_at=TODAY - timedelta(days=25),
        ),
        Subscription(
            user_id=users["demo"].id,
            catalog_service_id=catalog["ChatGPT Plus"].id,
            cost=20.00,
            renewal_date=TODAY + timedelta(days=20),
            is_trial=False,
            trial_expiration_date=None,
            enrolled_at=TODAY - timedelta(days=40),
        ),
        # alex: overlaps catalog with demo (many:many — same service, many users)
        Subscription(
            user_id=users["alex"].id,
            catalog_service_id=catalog["Spotify"].id,
            cost=10.99,
            renewal_date=TODAY + timedelta(days=18),
            is_trial=False,
            trial_expiration_date=None,
            enrolled_at=TODAY - timedelta(days=120),
        ),
        Subscription(
            user_id=users["alex"].id,
            catalog_service_id=catalog["Adobe Creative Cloud"].id,
            cost=54.99,
            renewal_date=TODAY + timedelta(days=3),
            is_trial=False,
            trial_expiration_date=None,
            enrolled_at=TODAY - timedelta(days=200),
        ),
        Subscription(
            user_id=users["alex"].id,
            catalog_service_id=catalog["Notion"].id,
            cost=0.0,
            renewal_date=TODAY + timedelta(days=9),
            is_trial=True,
            trial_expiration_date=TODAY + timedelta(days=9),
            enrolled_at=TODAY - timedelta(days=5),
        ),
        # sam: Disney+ also used alone; ChatGPT shared with demo
        Subscription(
            user_id=users["sam"].id,
            catalog_service_id=catalog["Disney+"].id,
            cost=9.99,
            renewal_date=TODAY + timedelta(days=8),
            is_trial=False,
            trial_expiration_date=None,
            enrolled_at=TODAY - timedelta(days=60),
        ),
        Subscription(
            user_id=users["sam"].id,
            catalog_service_id=catalog["ChatGPT Plus"].id,
            cost=0.0,
            renewal_date=TODAY + timedelta(days=2),
            is_trial=True,
            trial_expiration_date=TODAY + timedelta(days=2),
            enrolled_at=TODAY - timedelta(days=12),
        ),
        # admin has no subscriptions — still has 1:1 profile
    ]
    db.session.add_all(rows)
    db.session.commit()
    return rows


def main():
    with app.app_context():
        clear_tables()
        users = seed_users()
        catalog = seed_catalog()
        subscriptions = seed_subscriptions(users, catalog)

        print(
            f"Seeded {User.query.count()} users, "
            f"{Profile.query.count()} profiles (1:1), "
            f"{CatalogService.query.count()} catalog services, "
            f"{Subscription.query.count()} subscriptions "
            f"(1:many + many:many association)."
        )
        print(
            "Accounts -> admin/admin123 (admin), demo/demo123, "
            "alex/alex123, sam/sam1234"
        )
        # Sanity: Spotify has multiple users (many:many)
        spotify_users = len(catalog["Spotify"].users)
        print(f"Spotify tracked by {spotify_users} users (many:many check).")
        print(f"demo subscriptions: {len(users['demo'].subscriptions)} (1:many check).")
        print(f"demo profile: {users['demo'].profile.display_name} (1:1 check).")
        assert len(subscriptions) == 8
        assert all(u.profile is not None for u in users.values())
        assert spotify_users >= 2


if __name__ == "__main__":
    main()
