import os
import re
from functools import wraps
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from sqlalchemy import URL, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    watchlist = db.relationship("Watchlist", cascade="all, delete-orphan", back_populates="user")


class Title(db.Model):
    __tablename__ = "titles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(100))
    language = db.Column(db.String(60))
    year = db.Column(db.Integer)
    duration = db.Column(db.String(30))
    rating = db.Column(db.Numeric(3, 1), default=0)
    poster = db.Column(db.String(600))
    backdrop = db.Column(db.String(600))
    featured = db.Column(db.Boolean, default=False)
    watchlist_entries = db.relationship("Watchlist", cascade="all, delete-orphan", back_populates="title")


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title_id = db.Column(db.Integer, db.ForeignKey("titles.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    __table_args__ = (db.UniqueConstraint("user_id", "title_id", name="unique_watch"),)
    user = db.relationship("User", back_populates="watchlist")
    title = db.relationship("Title", back_populates="watchlist_entries")


SEED_TITLES = [
    {
        "title": "The Last Horizon",
        "description": "A former astronaut discovers a signal beyond the edge of the solar system and returns to space to uncover its source.",
        "genre": "Sci-Fi • Adventure", "language": "English", "year": 2026, "duration": "2h 18m",
        "rating": 8.7, "poster": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=700&q=85",
        "backdrop": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=1800&q=85", "featured": True,
    },
    {
        "title": "Shadow Protocol",
        "description": "An intelligence analyst races against time after a classified operation is exposed.",
        "genre": "Action • Thriller", "language": "English", "year": 2026, "duration": "2h 05m",
        "rating": 8.3, "poster": "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=700&q=85",
        "backdrop": "https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&w=1800&q=85", "featured": True,
    },
    {
        "title": "The Family Table",
        "description": "Three generations return to their hometown for a celebration that changes all of them.",
        "genre": "Drama • Family", "language": "Tamil", "year": 2025, "duration": "1h 58m",
        "rating": 8.1, "poster": "https://images.unsplash.com/photo-1515003197210-e0cd71810b5f?auto=format&fit=crop&w=700&q=85",
        "backdrop": "https://images.unsplash.com/photo-1478145046317-39f10e56b5e9?auto=format&fit=crop&w=1800&q=85", "featured": False,
    },
    {
        "title": "Midnight Run",
        "description": "Two unlikely friends take one night-long road trip that turns into a hilarious adventure.",
        "genre": "Comedy", "language": "Hindi", "year": 2025, "duration": "1h 49m",
        "rating": 7.9, "poster": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=700&q=85",
        "backdrop": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1800&q=85", "featured": False,
    },
    {
        "title": "Wild Earth",
        "description": "A cinematic journey through forests, oceans and remote landscapes.",
        "genre": "Documentary", "language": "English", "year": 2026, "duration": "1h 35m",
        "rating": 9.0, "poster": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=700&q=85",
        "backdrop": "https://images.unsplash.com/photo-1473445361085-b9a07f55608b?auto=format&fit=crop&w=1800&q=85", "featured": False,
    },
    {
        "title": "Champions",
        "description": "An underdog team gets one final chance to change its story.",
        "genre": "Sports • Drama", "language": "English", "year": 2025, "duration": "2h 02m",
        "rating": 8.0, "poster": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=700&q=85",
        "backdrop": "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&w=1800&q=85", "featured": False,
    },
]


def database_uri():
    uri = os.getenv("DATABASE_URL")
    if uri:
        return uri.replace("mysql://", "mysql+mysqlconnector://", 1)
    if os.getenv("DB_HOST"):
        return str(URL.create(
            "mysql+mysqlconnector",
            username=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            database=os.getenv("DB_NAME", "primeflix"),
        ))
    return str(URL.create("sqlite", database=str(Path(__file__).resolve().parent / "instance" / "primeflix.db")))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY") or ("development-only-change-me" if os.getenv("APP_ENV") != "production" else None),
        SQLALCHEMY_DATABASE_URI=database_uri(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("APP_ENV") == "production",
    )
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY before running in production.")

    configured_database = app.config["SQLALCHEMY_DATABASE_URI"]
    if getattr(configured_database, "drivername", "").startswith("sqlite") or str(configured_database).startswith("sqlite:"):
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()
        if db.session.scalar(select(db.func.count()).select_from(Title)) == 0:
            db.session.add_all(Title(**title) for title in SEED_TITLES)
            db.session.commit()

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session:
                flash("Please sign in to continue.", "warning")
                return redirect(url_for("login"))
            return view(*args, **kwargs)
        return wrapped

    @app.route("/")
    def home():
        titles = db.session.scalars(select(Title).order_by(Title.featured.desc(), Title.id.desc())).all()
        return render_template("index.html", titles=titles)

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")
            confirm = request.form.get("confirm_password", "")
            if not all((name, email, phone, password, confirm)):
                flash("Please fill in all fields.", "danger")
            elif len(name) > 100 or len(phone) > 20 or len(email) > 150 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                flash("Enter a valid name, email, and phone number.", "danger")
            elif password != confirm:
                flash("Passwords do not match.", "danger")
            elif len(password) < 8:
                flash("Password must contain at least 8 characters.", "danger")
            else:
                try:
                    db.session.add(User(name=name, email=email, phone=phone, password_hash=generate_password_hash(password)))
                    db.session.commit()
                    flash("Account created successfully. Please sign in.", "success")
                    return redirect(url_for("login"))
                except IntegrityError:
                    db.session.rollback()
                    flash("An account with this email already exists.", "warning")
                except SQLAlchemyError:
                    db.session.rollback()
                    app.logger.exception("Unable to create account")
                    flash("Unable to create your account right now. Please try again.", "danger")
        return render_template("signup.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            try:
                user = db.session.scalar(select(User).where(User.email == email))
            except SQLAlchemyError:
                app.logger.exception("Unable to look up account")
                flash("Sign in is temporarily unavailable. Please try again.", "danger")
                return render_template("login.html"), 503
            if user and check_password_hash(user.password_hash, password):
                session.clear()
                session["user_id"] = user.id
                session["user_name"] = user.name
                flash("Welcome back!", "success")
                return redirect(url_for("home"))
            flash("Invalid email or password.", "danger")
        return render_template("login.html")

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        flash("You have been signed out.", "success")
        return redirect(url_for("home"))

    @app.route("/title/<int:title_id>")
    def title_details(title_id):
        title = db.session.get(Title, title_id)
        if not title:
            flash("Title not found.", "danger")
            return redirect(url_for("home"))
        return render_template("details.html", title=title)

    @app.route("/watchlist")
    @login_required
    def watchlist():
        entries = db.session.scalars(
            select(Watchlist).where(Watchlist.user_id == session["user_id"]).order_by(Watchlist.created_at.desc())
        ).all()
        return render_template("watchlist.html", titles=[entry.title for entry in entries])

    @app.route("/watchlist/toggle/<int:title_id>", methods=["POST"])
    @login_required
    def toggle_watchlist(title_id):
        title = db.session.get(Title, title_id)
        if title is None:
            flash("Title not found.", "danger")
            return redirect(request.referrer or url_for("home"))
        entry = db.session.scalar(
            select(Watchlist).where(Watchlist.user_id == session["user_id"], Watchlist.title_id == title_id)
        )
        if entry:
            db.session.delete(entry)
            message = "Removed from your list."
        else:
            db.session.add(Watchlist(user_id=session["user_id"], title_id=title_id))
            message = "Added to your list."
        db.session.commit()
        flash(message, "success")
        return redirect(request.referrer or url_for("home"))

    @app.route("/api/search")
    def search():
        query = request.args.get("q", "").strip()
        if len(query) < 2:
            return jsonify([])
        try:
            titles = db.session.scalars(
                select(Title)
                .where(
                    Title.title.contains(query, autoescape=True)
                    | Title.genre.contains(query, autoescape=True)
                    | Title.language.contains(query, autoescape=True)
                )
                .order_by(Title.featured.desc())
                .limit(10)
            ).all()
            return jsonify([{
                "id": title.id, "title": title.title, "genre": title.genre,
                "language": title.language, "year": title.year,
            } for title in titles])
        except SQLAlchemyError:
            app.logger.exception("Search failed")
            return jsonify({"error": "Search is temporarily unavailable."}), 503

    @app.route("/health")
    def health():
        try:
            db.session.execute(db.select(1))
            return jsonify({"status": "ok", "database": "connected"})
        except SQLAlchemyError:
            app.logger.exception("Database health check failed")
            return jsonify({"status": "error", "database": "disconnected"}), 503

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
