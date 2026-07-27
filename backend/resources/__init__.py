from resources.admin import AdminUsers
from resources.auth import AvatarUpload, Login, Me, Refresh, Register
from resources.catalog import CatalogDetail, CatalogList, CatalogSubscribers
from resources.dashboard import AdminAnalytics, Dashboard
from resources.subscriptions import SubscriptionDetail, SubscriptionList


def register_resources(api):
    """Register Flask-RESTful resources on the API."""
    api.add_resource(Register, "/auth/register")
    api.add_resource(Login, "/auth/login")
    api.add_resource(Refresh, "/auth/refresh")
    api.add_resource(Me, "/auth/me")
    api.add_resource(AvatarUpload, "/auth/me/avatar")

    api.add_resource(Dashboard, "/dashboard")
    api.add_resource(SubscriptionList, "/subscriptions")
    api.add_resource(SubscriptionDetail, "/subscriptions/<int:id>")

    api.add_resource(CatalogList, "/catalog")
    api.add_resource(CatalogDetail, "/catalog/<int:id>")
    api.add_resource(CatalogSubscribers, "/catalog/<int:id>/subscribers")

    api.add_resource(AdminUsers, "/admin/users")
    api.add_resource(AdminAnalytics, "/admin/analytics")
