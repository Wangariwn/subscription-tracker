# Subscription & Free Trial Tracker

Flask API for tracking recurring subscriptions and free trials.

## Tech Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy / Flask-Migrate
- Flask-JWT-Extended
- Flask-Marshmallow / Marshmallow-SQLAlchemy
- SQLite

## Models

| Table | Fields |
| --- | --- |
| **User** | `id`, `username`, `email`, `password_hash`, `role` (`user` \| `admin`) |
| **CatalogService** | `id`, `service_name`, `default_cost`, `category`, `default_trial_days` |
| **Subscription** | `id`, `user_id`, `service_name`, `cost`, `renewal_date`, `is_trial`, `trial_expiration_date` |

## Setup

```bash
pipenv install
pipenv shell
cd server
export FLASK_APP=app.py
export JWT_SECRET_KEY="change-me-in-production"

flask db upgrade
python seed.py
flask run --port=5555
```
