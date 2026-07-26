from resources.admin import AdminUsers
from resources.auth import Login, Me, Register


def register_resources(api):
    """Register Flask-RESTful resources on the API."""
    api.add_resource(Register, "/auth/register")
    api.add_resource(Login, "/auth/login")
    api.add_resource(Me, "/auth/me")
    api.add_resource(AdminUsers, "/admin/users")
