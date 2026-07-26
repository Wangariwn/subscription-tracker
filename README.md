# Subscription & Free Trial Tracker

A secure Flask web API that helps users manage recurring monthly bills, monitor active free trials, and avoid unexpected auto-renewal charges. Users track personal spending on a private dashboard, while admins maintain a global catalog of popular service templates.

## Features

- JWT authentication with hashed passwords (`werkzeug.security`)
- Role-based access control (`user` and `admin`)
- Personal subscription CRUD with data isolation
- Admin-managed global service catalog
- Admin analytics dashboard
- Free-trial expiration tracking and renewal awareness

## Tech Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy / Flask-Migrate
- Flask-JWT-Extended
- Flask-Marshmallow / Marshmallow-SQLAlchemy
- SQLite

## Database Models

| Table | Fields |
| --- | --- |
| **User** | `id`, `username`, `email`, `password_hash`, `role` (`user` \| `admin`) |
| **CatalogService** | `id`, `service_name`, `default_cost`, `category`, `default_trial_days` |
| **Subscription** | `id`, `user_id`, `service_name`, `cost`, `renewal_date`, `is_trial`, `trial_expiration_date` |

## Installation

```bash
pipenv install
pipenv shell
cd server
export FLASK_APP=app.py
export JWT_SECRET_KEY="change-me-in-production"

flask db init
flask db migrate -m "create users catalog subscriptions"
flask db upgrade

python seed.py
```

## Run

```bash
cd server
export FLASK_APP=app.py
export JWT_SECRET_KEY="change-me-in-production"

flask run --port=5555
# or
python app.py
```

API base URL: [http://127.0.0.1:5555](http://127.0.0.1:5555)

## API Endpoints

### Auth
| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Register a new user | Public |
| `POST` | `/auth/login` | Login and receive a JWT | Public |

### User (role: `user` or authenticated)
| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| `GET` | `/dashboard` | Personal dashboard (active subs, spend, trial alerts) | JWT |
| `GET` | `/subscriptions` | List current user's subscriptions | JWT |
| `GET` | `/subscriptions/<id>` | Show one of the current user's subscriptions | JWT |
| `POST` | `/subscriptions` | Create a subscription | JWT |
| `PATCH` | `/subscriptions/<id>` | Update a subscription | JWT |
| `DELETE` | `/subscriptions/<id>` | Delete a subscription | JWT |
| `GET` | `/catalog` | Browse global service catalog templates | JWT |

### Admin (role: `admin`)
| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| `GET` | `/admin/analytics` | Platform statistics | JWT + admin |
| `GET` | `/admin/catalog` | List catalog templates | JWT + admin |
| `POST` | `/admin/catalog` | Create a catalog template | JWT + admin |
| `PATCH` | `/admin/catalog/<id>` | Update a catalog template | JWT + admin |
| `DELETE` | `/admin/catalog/<id>` | Delete a catalog template | JWT + admin |

Admin-only routes return `403 Forbidden` for non-admin users.

## Default Seed Accounts

| Username | Password | Role |
| --- | --- | --- |
| `admin` | `admin123` | admin |
| `demo` | `demo123` | user |

Change these credentials before deploying.
