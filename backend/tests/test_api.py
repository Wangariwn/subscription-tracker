from datetime import date, timedelta

from tests.conftest import auth_header


def test_login_returns_access_and_refresh(client, seeded):
    response = client.post(
        "/auth/login",
        json={"username": "demo", "password": "demo123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json
    assert "refresh_token" in response.json
    assert response.json["user"]["username"] == "demo"


def test_protected_route_requires_token(client, seeded):
    response = client.get("/dashboard")
    assert response.status_code == 401


def test_dashboard_with_token(client, seeded):
    headers, _ = auth_header(client)
    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    assert response.json["total_subscriptions"] == 2
    assert "monthly_spend" in response.json


def test_admin_analytics_forbidden_for_user(client, seeded):
    headers, _ = auth_header(client, "demo", "demo123")
    response = client.get("/admin/analytics", headers=headers)
    assert response.status_code == 403


def test_admin_analytics_ok_for_admin(client, seeded):
    headers, _ = auth_header(client, "admin", "admin123")
    response = client.get("/admin/analytics", headers=headers)
    assert response.status_code == 200
    assert response.json["total_subscriptions"] == 2


def test_admin_subscriptions_forbidden_for_user(client, seeded):
    headers, _ = auth_header(client, "demo", "demo123")
    response = client.get("/admin/subscriptions", headers=headers)
    assert response.status_code == 403


def test_admin_subscriptions_lists_all(client, seeded):
    headers, _ = auth_header(client, "admin", "admin123")
    response = client.get("/admin/subscriptions", headers=headers)
    assert response.status_code == 200
    assert response.json["total"] == 2
    assert all("user" in item for item in response.json["items"])
    usernames = {item["user"]["username"] for item in response.json["items"]}
    assert "demo" in usernames


def test_refresh_token_issues_new_access(client, seeded):
    _, body = auth_header(client)
    refresh = body["refresh_token"]
    response = client.post(
        "/auth/refresh",
        headers={"Authorization": f"Bearer {refresh}"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json


def test_subscription_search_and_combined_filters(client, seeded):
    headers, _ = auth_header(client)
    response = client.get(
        "/subscriptions?q=spot&category=Music&is_trial=true&min_cost=0&max_cost=5",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["total"] == 1
    assert response.json["items"][0]["catalog_service"]["service_name"] == "Spotify"

    # Netflix renews in 10 days in seed data — window must include that date
    before = (date.today() + timedelta(days=14)).isoformat()
    response = client.get(
        f"/subscriptions?category=Streaming&renewing_before={before}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["total"] == 1
    assert response.json["items"][0]["catalog_service"]["service_name"] == "Netflix"


def test_subscription_pagination_metadata(client, seeded):
    headers, _ = auth_header(client)
    response = client.get("/subscriptions?page=1&per_page=1", headers=headers)
    assert response.status_code == 200
    assert response.json["per_page"] == 1
    assert response.json["total"] == 2
    assert response.json["total_pages"] == 2
    assert len(response.json["items"]) == 1
