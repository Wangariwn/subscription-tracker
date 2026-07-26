from flask import request

from resources.auth_helpers import error_response


def parse_pagination_args(default_per_page=10, max_per_page=50):
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", default_per_page))
    except (TypeError, ValueError):
        return None, None, error_response("page and per_page must be integers")

    if page < 1:
        return None, None, error_response("page must be >= 1")
    if per_page < 1 or per_page > max_per_page:
        return None, None, error_response(
            f"per_page must be between 1 and {max_per_page}"
        )
    return page, per_page, None


def paginated_response(pagination, items):
    return {
        "items": items,
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": pagination.pages,
    }
