#!/usr/bin/env python3
"""Lightweight API smoke tests (no pytest required)."""

from datetime import date, timedelta

from app import create_app
from config import TestConfig
from models import db, User, Profile, CatalogService, Subscription


def seed(app):
    with app.app_context():
        db.create_all()
        admin = User(username="admin", email="admin@example.com", role="admin")
        admin.set_password("admin123")
        admin.profile = Profile(display_name="Admin")
        demo = User(username="demo", email="demo@example.com", role="user")
        demo.set_password("demo123")
        demo.profile = Profile(display_name="Demo")
        netflix = CatalogService(
            service_name="Netflix",
            default_cost=15.49,
            category="Streaming",
            default_trial_days=30,
        )
        spotify = CatalogService(
            service_name="Spotify",
            default_cost=10.99,
            category="Music",
            default_trial_days=30,
        )
        db.session.add_all([admin, demo, netflix, spotify])
        db.session.commit()
        db.session.add_all(
            [
                Subscription(
                    user_id=demo.id,
                    catalog_service_id=netflix.id,
                    cost=15.49,
                    renewal_date=date.today() + timedelta(days=10),
                    is_trial=False,
                    enrolled_at=date.today() - timedelta(days=30),
                ),
                Subscription(
                    user_id=demo.id,
                    catalog_service_id=spotify.id,
                    cost=0.0,
                    renewal_date=date.today() + timedelta(days=5),
                    is_trial=True,
                    trial_expiration_date=date.today() + timedelta(days=5),
                    enrolled_at=date.today() - timedelta(days=10),
                ),
            ]
        )
        db.session.commit()


def main():
    app = create_app(TestConfig)
    client = app.test_client()
    with app.app_context():
        seed(app)

    failures = 0

    def check(name, condition, detail=""):
        nonlocal failures
        if condition:
            print(f"PASS  {name}")
        else:
            failures += 1
            print(f"FAIL  {name} {detail}")

    r = client.get("/dashboard")
    check("protected without token -> 401", r.status_code == 401, r.data)

    r = client.post("/auth/login", json={"username": "demo", "password": "demo123"})
    check("login returns tokens", r.status_code == 200 and "refresh_token" in r.json, r.data)
    access = r.json["access_token"]
    refresh = r.json["refresh_token"]
    h = {"Authorization": f"Bearer {access}"}

    r = client.get("/dashboard", headers=h)
    check("dashboard ok", r.status_code == 200 and r.json["total_subscriptions"] == 2, r.data)

    r = client.get("/admin/analytics", headers=h)
    check("user forbidden on analytics", r.status_code == 403, r.data)

    r = client.post("/auth/refresh", headers={"Authorization": f"Bearer {refresh}"})
    check("refresh issues access token", r.status_code == 200 and "access_token" in r.json, r.data)

    r = client.get(
        "/subscriptions?q=spot&category=Music&is_trial=true&min_cost=0&max_cost=5",
        headers=h,
    )
    check(
        "combined search/filters",
        r.status_code == 200 and r.json["total"] == 1,
        r.data,
    )

    r = client.get("/subscriptions?page=1&per_page=1", headers=h)
    check(
        "pagination metadata",
        r.status_code == 200 and r.json["total_pages"] == 2,
        r.data,
    )

    print("---")
    if failures:
        raise SystemExit(f"{failures} failure(s)")
    print("All smoke tests passed.")


if __name__ == "__main__":
    main()
