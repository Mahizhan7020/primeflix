# 🎬 PrimeFlix

A full-stack movie-catalog website inspired by popular streaming platforms. Built as an academic website project with a Flask backend, account authentication, persistent database storage, and personal watchlists.

## 🚀 Live Project

**Live website:** [https://primeflix-1.onrender.com](https://primeflix-1.onrender.com)

## 📌 Project Overview

PrimeFlix recreates the core experience of a movie-streaming catalog. Visitors can browse titles, search the catalog, create an account, and sign in. Signed-in users can manage a personal watchlist.

### Features

- Responsive movie-catalog landing page and title details
- Account registration, sign-in, and sign-out
- Secure password hashing and session-based authentication
- CSRF protection for forms that change data
- Search by title, genre, or language
- Personal watchlist with add and remove actions
- SQLite for local development and MySQL for the hosted service

## 🛠️ Technologies

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask, Gunicorn
- **Database:** SQLAlchemy, SQLite, MySQL Connector/Python
- **Security:** Werkzeug password hashing, Flask sessions, CSRF protection, environment-based secrets
- **Hosting:** GitHub, Render, Clever Cloud MySQL

## 📁 Project Structure

```text
primeflix/
├── app.py
├── main.py
├── Procfile
├── railway.json
├── render.yaml
├── requirements.txt
├── .env.example
├── README.md
├── static/
│   ├── css/
│   └── js/
├── templates/
└── tests/
```

The database tables and starter catalog are initialized by the application. You do not need to run a SQL schema manually.

## ⚙️ Run Locally

Requires Python 3.10 or newer.

1. Clone the repository and enter its folder:

   ```powershell
   git clone https://github.com/Mahizhan7020/primeflix.git
   cd primeflix
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies and create your local environment file:

   ```powershell
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

4. Start the application:

   ```powershell
   python app.py
   ```

5. Open <http://127.0.0.1:5000>.

By default, local development uses `instance/primeflix.db` and seeds the catalog automatically. To use a local or hosted MySQL database during development, set `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, and `DB_PORT` in `.env`.

## ☁️ Deployment

The production setup uses Render for the Flask web service and Clever Cloud for MySQL:

```text
GitHub → Render web service → Clever Cloud MySQL
```

The Render blueprint is [render.yaml](./render.yaml). Its build and start commands are:

```text
pip install -r requirements.txt
gunicorn app:app
```

Set these environment variables in the Render service using the values from the Clever Cloud MySQL add-on:

```text
APP_ENV=production
SECRET_KEY=<a private random secret>
DB_HOST=<Clever Cloud host>
DB_NAME=<Clever Cloud database name>
DB_USER=<Clever Cloud username>
DB_PASSWORD=<Clever Cloud password>
DB_PORT=<Clever Cloud port>
```

Render generates `SECRET_KEY` when the service is created from the blueprint. Keep all credentials private; never commit `.env` or production secrets to GitHub. The deployed health check is available at <https://primeflix-1.onrender.com/health>.

The free Render web service can sleep when idle, and its filesystem is temporary. The production MySQL database stores accounts and watchlists persistently.

## 🧪 Tests

Run the test suite with:

```powershell
python -m unittest discover -s tests -v
```

## 🎓 Academic Project

| Requirement | Implementation |
| --- | --- |
| Home page | PrimeFlix movie catalog |
| Sign-up and log-in pages | Functional account registration and authentication |
| Secure passwords | Werkzeug password hashing |
| Persistent database | SQLite locally; Clever Cloud MySQL in production |
| Additional feature | Search and personal watchlists |
| Public deployment | Render |

PrimeFlix is an educational project and is not affiliated with or endorsed by any commercial streaming service.

**Author:** [Mahizhan7020](https://github.com/Mahizhan7020)
