# Subscription & Free Trial Tracker

Flask API for tracking recurring subscriptions and free trials.

## Backend structure

```
backend/
├── app.py            # app factory, register blueprints/resources
├── config.py         # config from environment
├── models.py         # SQLAlchemy models + serialize rules
├── seed.py           # seed script
├── resources/        # Flask-RESTful resources
├── migrations/       # Flask-Migrate
├── .env              # SECRET_KEY, DATABASE_URI, JWT_SECRET (git-ignored)
└── requirements.txt
```

## Tech Stack

- Python 3.12
- Flask / Flask-RESTful
- Flask-SQLAlchemy / Flask-Migrate
- Flask-JWT-Extended / Flask-CORS
- SQLAlchemy-Serializer
- python-dotenv
- SQLite (dev) / PostgreSQL (`psycopg2-binary`)

## Models

| Table | Fields |
| --- | --- |
| **User** | `id`, `username`, `email`, `password_hash`, `role` (`user` \| `admin`) |
| **Profile** | `id`, `user_id` (unique), `display_name`, `bio`, `preferred_currency`, `timezone` |
| **CatalogService** | `id`, `service_name`, `default_cost`, `category`, `default_trial_days` |
| **Subscription** | `id`, `user_id`, `catalog_service_id`, `cost`, `renewal_date`, `is_trial`, `trial_expiration_date`, `enrolled_at` |

### Relationships

| Type | Mapping |
| --- | --- |
| **1:1** | `User` ↔ `Profile` (`uselist=False`, unique `user_id`) |
| **1:many** | `User` → many `Subscription`s |
| **many:many** | `User` ↔ `CatalogService` via `Subscription` association object (extra: `cost`, dates, `enrolled_at`) |

### Why these relationships (oral defense)

- **1:1 User ↔ Profile** — auth fields stay on `User`; display preferences live on `Profile` with a **unique** `user_id` and `uselist=False`. Deleting a user cascades the profile.
- **1:many User → Subscription** — one account owns many tracked bills. Queries always scope by `user_id` so users cannot read or mutate someone else’s rows.
- **many:many User ↔ CatalogService via Subscription** — many people can track Netflix; one person can track many services. `Subscription` is an **association object** (not a bare join table) because enrolment carries **extra data**: `cost`, `renewal_date`, `is_trial`, `trial_expiration_date`, `enrolled_at`. Unique `(user_id, catalog_service_id)` prevents duplicate tracking.

Serialization uses `serialize_rules` to cut recursion (`-user.subscriptions`, `-catalog_service.subscriptions`, `-password_hash`). Nested `catalog_service` is attached deliberately in resource serializers when needed.

### Deep queries (oral defense)

| Endpoint | What the query does |
| --- | --- |
| `GET /dashboard` | Eager-loads `catalog_service` (`joinedload`), sums non-trial `cost` with `func.sum`, filters trial alerts by date window |
| `GET /subscriptions?category=` | Relationship filter via `.has(CatalogService.category == …)`, `order_by(renewal_date)`, `.paginate()` |
| `GET /catalog/<id>/subscribers` | Joins association rows to `User` + `Profile` for one catalog service (many:many side) |
| `GET /admin/analytics` | `join` + `group_by` category / service, `having(count >= 1)`, `func.sum`/`func.count`, and `User.subscriptions.any(is_trial)` |

List endpoints never load-all-then-slice: they use SQLAlchemy `.paginate(page=…, per_page=…)`.

## Frontend structure

```
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/        # useAuth, useFetch
│   ├── context/      # AuthContext holding the JWT
│   └── App.jsx
└── vite.config.js
```

## Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

export FLASK_APP=app.py
flask db upgrade
python seed.py
flask run --port=5555
```

Default seed accounts: `admin` / `admin123` (admin), `demo` / `demo123`, `alex` / `alex123`, `sam` / `sam1234`.

### Auth endpoints

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/auth/register` | Public | Register user + 1:1 profile (hashed password) |
| `POST` | `/auth/login` | Public | Login; returns JWT `access_token` |
| `GET` | `/auth/me` | JWT | Current user + profile |
| `GET` | `/admin/users` | JWT + admin | List users (`403` for non-admins) |

Send `Authorization: Bearer <token>` on protected routes.

### User endpoints

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/dashboard` | JWT | Spend aggregate, trials, upcoming renewals (eager-loaded) |
| `GET` | `/subscriptions?page=&per_page=&category=&is_trial=` | JWT | Paginated list; filter across catalog category |
| `POST` | `/subscriptions` | JWT | Create subscription (association row) |
| `GET` | `/subscriptions/<id>` | JWT | Show own subscription |
| `PATCH` | `/subscriptions/<id>` | JWT | Update own subscription |
| `DELETE` | `/subscriptions/<id>` | JWT | Delete own subscription |
| `GET` | `/catalog?page=&per_page=&category=` | JWT | Paginated catalog browse |
| `GET` | `/catalog/<id>` | JWT | Catalog detail |
| `GET` | `/catalog/<id>/subscribers` | JWT | Users tracking a service (join + profile) |

Paginated responses include `items`, `total`, `page`, `per_page`, `total_pages`.

### Admin endpoints

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/admin/users` | JWT + admin | List users |
| `GET` | `/admin/analytics` | JWT + admin | Aggregates: `count`/`sum`/`group_by`/`having`, `.any()` trials |
| `POST` | `/catalog` | JWT + admin | Create catalog template |
| `PATCH` | `/catalog/<id>` | JWT + admin | Update catalog template |
| `DELETE` | `/catalog/<id>` | JWT + admin | Delete catalog template |

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies `/api` → `http://127.0.0.1:5555`.

Frontend routes: `/login`, `/register`, protected `/` (dashboard), `/subscriptions` (CRUD), `/subscriptions/new`, `/subscriptions/:id/edit`, and `/catalog`. JWT is stored in `localStorage` and attached as `Authorization: Bearer …`.

Frontend data flow: `fetch` only (no axios), `AuthContext` holds the JWT, `useFetch` / `useApi` custom hooks, and every request surface shows **loading / error / success**. Unauthenticated visits to protected routes redirect to `/login`.

## Requirement checklist

| Requirement | Where it lives |
| --- | --- |
| JWT auth + hashed passwords | `resources/auth.py`, `User.set_password` (werkzeug) |
| Roles (user vs admin) | `admin_required`, `/admin/*`, catalog writes |
| 1:1 / 1:many / many:many | `models.py` + seed associations |
| Pagination metadata | `resources/pagination.py` + list endpoints |
| Deep queries (≥3) | dashboard, filtered subscriptions, subscribers, analytics |
| Migrations + seed | `migrations/`, `seed.py` |
| Frontend fetch + hooks + CRUD | `frontend/src/pages/*`, `hooks/*` |
| Protected frontend routes | `components/ProtectedRoute.jsx` |
