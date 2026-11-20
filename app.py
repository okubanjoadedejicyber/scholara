
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, UserMixin, login_user, logout_user, login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from scholarship_services import discover_scholarships

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "scholara-development-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///scholara.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# STUDENT DATABASE MODEL
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    education_level = db.Column(db.String(50))
    institution = db.Column(db.String(150))


# Load logged-in student
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# HOME PAGE
@app.route("/")
def index():
    return render_template("index.html")


# STUDENT REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        education_level = request.form.get("education_level", "")
        institution = request.form.get("institution", "")

        if not full_name or not email or not password:
            flash("Please complete all required fields.", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("This email is already registered.", "warning")
            return redirect(url_for("register"))

        new_user = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            education_level=education_level,
            institution=institution
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# STUDENT LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("opportunities"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# STUDENT LOGOUT
@app.route("/logout")
@login_required
def logout():

    logout_user()
    flash("You have logged out.", "info")

    return redirect(url_for("index"))


# # SCHOLARSHIP OPPORTUNITIES
# @app.route("/opportunities")
# @login_required
# def opportunities():

#     return render_template("opportunities.html")


# STUDENT PROFILE
@app.route("/profile")
@login_required
def profile():

    return render_template("profile.html")


# SCHOLARSHIP ANALYSIS
@app.route("/analyse")
@login_required
def analyse():

    return render_template("analyse.html")


# APPLICATION INFORMATION
@app.route("/application")
@login_required
def application():

    return render_template("application.html")


# DISCOVER SCHOLARSHIPS
@app.route("/discover", methods=["GET", "POST"])
def discover():

    scholarships = []
    error = None

    if request.method == "POST":
        try:
            scholarships = discover_scholarships()

            if not scholarships:
                error = "No scholarships found. Please try again later."

        except Exception as e:
            print("Discovery error:", e)
            error = "Unable to discover scholarships at the moment."

    return render_template(
        "discover.html",
        scholarships=scholarships,
        error=error
    )

# Error Handling
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404


# CREATE DATABASE AND RUN APPLICATION
with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run(debug=True)
