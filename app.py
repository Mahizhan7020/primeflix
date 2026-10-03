import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    try:
        db=get_db(); cur=db.cursor(dictionary=True)
        cur.execute("SELECT * FROM titles ORDER BY featured DESC, id DESC")
        titles=cur.fetchall(); cur.close(); db.close()
    except Error as e:
        print("MYSQL ERROR:", e); titles=[]
        flash("Database connection failed. Check your .env settings.", "danger")
    return render_template("index.html", titles=titles)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        name=request.form.get("name","").strip()
        email=request.form.get("email","").strip().lower()
        phone=request.form.get("phone","").strip()
        password=request.form.get("password","")
        confirm=request.form.get("confirm_password","")
        if not all([name,email,phone,password,confirm]):
            flash("Please fill in all fields.","danger"); return render_template("signup.html")
        if password != confirm:
            flash("Passwords do not match.","danger"); return render_template("signup.html")
        if len(password)<6:
            flash("Password must contain at least 6 characters.","danger"); return render_template("signup.html")
        try:
            db=get_db(); cur=db.cursor(dictionary=True)
            cur.execute("SELECT id FROM users WHERE email=%s",(email,))
            if cur.fetchone():
                flash("An account with this email already exists.","warning")
                cur.close(); db.close(); return render_template("signup.html")
            cur.execute("INSERT INTO users (name,email,phone,password_hash) VALUES (%s,%s,%s,%s)",
                        (name,email,phone,generate_password_hash(password)))
            db.commit(); cur.close(); db.close()
            flash("Account created successfully. Please sign in.","success")
            return redirect(url_for("login"))
        except Error as e:
            print("MYSQL ERROR:",e); flash("Unable to create account.","danger")
    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email","").strip().lower()
        password=request.form.get("password","")
        try:
            db=get_db(); cur=db.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE email=%s",(email,))
            user=cur.fetchone(); cur.close(); db.close()
            if user and check_password_hash(user["password_hash"],password):
                session["user_id"]=user["id"]; session["user_name"]=user["name"]
                flash("Welcome back!","success"); return redirect(url_for("home"))
            flash("Invalid email or password.","danger")
        except Error as e:
            print("MYSQL ERROR:",e); flash("Database connection failed.","danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear(); flash("You have been signed out.","success")
    return redirect(url_for("home"))

@app.route("/title/<int:title_id>")
def title_details(title_id):
    try:
        db=get_db(); cur=db.cursor(dictionary=True)
        cur.execute("SELECT * FROM titles WHERE id=%s",(title_id,))
        title=cur.fetchone(); cur.close(); db.close()
    except Error as e:
        print("MYSQL ERROR:",e); title=None
    if not title:
        flash("Title not found.","danger"); return redirect(url_for("home"))
    return render_template("details.html",title=title)

@app.route("/watchlist")
@login_required
def watchlist():
    try:
        db=get_db(); cur=db.cursor(dictionary=True)
        cur.execute("""SELECT t.* FROM watchlist w JOIN titles t ON t.id=w.title_id
                       WHERE w.user_id=%s ORDER BY w.created_at DESC""",(session["user_id"],))
        titles=cur.fetchall(); cur.close(); db.close()
    except Error as e:
        print("MYSQL ERROR:",e); titles=[]; flash("Unable to load your list.","danger")
    return render_template("watchlist.html",titles=titles)

@app.route("/watchlist/toggle/<int:title_id>",methods=["POST"])
@login_required
def toggle_watchlist(title_id):
    try:
        db=get_db(); cur=db.cursor(dictionary=True)
        cur.execute("SELECT id FROM watchlist WHERE user_id=%s AND title_id=%s",
                    (session["user_id"],title_id))
        row=cur.fetchone()
        if row:
            cur.execute("DELETE FROM watchlist WHERE id=%s",(row["id"],))
            message="Removed from your list."
        else:
            cur.execute("INSERT INTO watchlist (user_id,title_id) VALUES (%s,%s)",
                        (session["user_id"],title_id))
            message="Added to your list."
        db.commit(); cur.close(); db.close(); flash(message,"success")
    except Error as e:
        print("MYSQL ERROR:",e); flash("Could not update your list.","danger")
    return redirect(request.referrer or url_for("home"))

@app.route("/api/search")
def search():
    q=request.args.get("q","").strip()
    if len(q)<2: return jsonify([])
    try:
        db=get_db(); cur=db.cursor(dictionary=True)
        cur.execute("""SELECT id,title,genre,language,year FROM titles
                       WHERE title LIKE %s OR genre LIKE %s OR language LIKE %s
                       ORDER BY featured DESC LIMIT 10""",
                    (f"%{q}%",f"%{q}%",f"%{q}%"))
        rows=cur.fetchall(); cur.close(); db.close(); return jsonify(rows)
    except Error as e:
        print("MYSQL ERROR:",e); return jsonify([])
@app.route("/health")
def health():
    try:
        db = get_db()
        db.close()
        return jsonify({
            "status": "ok",
            "database": "connected"
        })
    except Error as e:
        print("MYSQL ERROR:", e)
        return jsonify({
            "status": "error",
            "database": "disconnected"
        }), 500
if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0",port=int(os.getenv("PORT",5000)))
