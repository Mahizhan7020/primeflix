# PrimeFlix — Flask + MySQL streaming project

Amazon Prime Video-inspired educational project using HTML, CSS, JavaScript, Flask and MySQL.

Features:
- Landing/home page
- Sign up and login
- Secure password hashing
- MySQL persistence
- Search
- Title details
- My List/watchlist persisted in MySQL
- Add/remove from My List
- Responsive UI

Setup:
1. Install Python 3.10+.
2. `python -m venv venv`
3. Windows: `venv\\Scripts\\activate`
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`.
6. Put your MySQL/Clever Cloud credentials in `.env`.
7. Run `schema.sql` on your database.
8. `python app.py`
9. Open http://127.0.0.1:5000

For Clever Cloud use DB_HOST, DB_USER, DB_PASSWORD, DB_NAME and DB_PORT from the MySQL add-on.

Production command: `gunicorn app:app`

Never upload `.env` to GitHub.

This is a fictional educational streaming site inspired by common streaming-service layouts; it does not use Amazon Prime Video private APIs, source code or private assets.
