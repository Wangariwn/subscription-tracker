import pytest

from app import create_app
from config import TestConfig
from models import db, User, Profile, CatalogService, Subscription
from datetime import date, timedelta


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seeded(app):
    with app.app_context():
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

        sub = Subscription(
            user_id=demo.id,
            catalog_service_id=netflix.id,
            cost=15.49,
            renewal_date=date.today() + timedelta(days=10),
            is_trial=False,
            enrolled_at=date.today() - timedelta(days=30),
        )
        trial = Subscription(
            user_id=demo.id,
            catalog_service_id=spotify.id,
            cost=0.0,
            renewal_date=date.today() + timedelta(days=5),
            is_trial=True,
            trial_expiration_date=date.today() + timedelta(days=5),
            enrolled_at=date.today() - timedelta(days=10),
        )
        db.session.add_all([sub, trial])
        db.session.commit()
        return {"demo_id": demo.id, "netflix_id": netflix.id}


def auth_header(client, username="demo", password="demo123"):
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    token = response.json["access_token"]
    return {"Authorization": f"Bearer {token}"}, response.json
