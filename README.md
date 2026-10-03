# PrimeFlix

PrimeFlix is a fictional, responsive streaming-catalog demo built with Flask, SQLAlchemy, and a persistent database. It includes a home page, real account registration and login, title search/details, and a personal watchlist.

## Features

- Sign up and sign in with Werkzeug password hashing (passwords are never stored in plaintext).
- CSRF protection on every form that changes data.
- Persistent users, movie titles, and per-user watchlists.
- Search by title, genre, or language.
- SQLite for a zero-configuration local run; MySQL is supported for hosted deployments.
- Responsive home, account, title-details, and watchlist pages.

## Run locally

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open <http://127.0.0.1:5000>. By default, the app creates `instance/primeflix.db` and seeds the catalog on its first run. That SQLite database is persistent across restarts and is ignored by Git.

For MySQL, set `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and `DB_PORT` in `.env`; the tables and initial catalog are created automatically. Alternatively, set `DATABASE_URL` to a SQLAlchemy MySQL URL such as `mysql://user:password@host:3306/primeflix`. URL-encode special characters in credentials.

## Deploy

The included `render.yaml` configures a free Render web-service instance. Create a MySQL database with a provider that permits external connections, then set `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and `DB_PORT` in the Render service environment using that database's connection details. Render generates a strong `SECRET_KEY` from the blueprint. Keep `APP_ENV=production` so secure session cookies are enabled. The service exposes `/health` for a database-backed health check.

Free web-service instances may sleep when idle and have an ephemeral filesystem, so keep the database on an external MySQL service rather than relying on local SQLite for deployed accounts and watchlists. A public deployment requires a hosting account and a provisioned MySQL database. No public URL is available until those external services are configured.

## Tests

```powershell
python -m unittest discover -s tests -v
```

This is a fictional educational streaming catalog, not affiliated with or using private APIs or assets from a commercial streaming service.
