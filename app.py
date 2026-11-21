
import secrets

from flask import request, session, render_template, redirect, url_for, flash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

load_dotenv()

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

database_url = os.getenv("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql://", 1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "pool_timeout": 30,
}


from scholarship_services import (
    discover_scholarships,
    match_scholarship,
    analyse_with_ai,
)


db = SQLAlchemy(app)

# Import models after db has been initialized
import models


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def login_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("signin"))
        return route(*args, **kwargs)
    return wrapper


def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return None

    return models.User.query.get(user_id)

@app.context_processor
def inject_current_user():
    return dict(current_user=get_current_user())



# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
@limiter.limit("3 per minute", methods=["POST"])
def signup():

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validate required fields
        if not full_name or not email or not password:
            return render_template(
                "signup.html",
                error="Please fill in all fields."
            )

        # Validate password length
        if len(password) < 8:
            return render_template(
                "signup.html",
                error="Your password must be at least 8 characters."
            )

        # Check if account already exists
        existing_user = models.User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return render_template(
                "signup.html",
                error="An account with this email already exists."
            )

        # Split full name
        name_parts = full_name.split()

        first_name = name_parts[0]
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Hash password
        hashed_password = generate_password_hash(password)

        try:

            user = models.User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=hashed_password
            )

            db.session.add(user)
            db.session.flush()

            # Create student profile
            profile = models.StudentProfile(
                user_id=user.id
            )

            db.session.add(profile)

            db.session.commit()

            # Login user
            session.clear()
            session["user_id"] = user.id
            session["first_name"] = user.first_name

            return redirect(url_for("dashboard"))

        except Exception as e:

            db.session.rollback()

            print("SIGNUP ERROR:", e)

            return render_template(
                "signup.html",
                error="Something went wrong creating your account. Please try again."
            )

    return render_template("signup.html")



# --------------------------------------------------
# SIGNIN
# --------------------------------------------------

@app.route("/signin", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def signin():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template(
                "signin.html",
                error="Please enter your email and password."
            )

        user = models.User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password_hash, password
        ):

            session.clear()
            session["user_id"] = user.id
            session["first_name"] = user.first_name

            return redirect(url_for("dashboard"))

        return render_template(
            "signin.html",
            error="Invalid email or password."
        )

    return render_template("signin.html")


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/app/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    saved_count = models.SavedScholarship.query.filter_by(
        user_id=user.id
    ).count()

    application_count = models.Application.query.filter_by(
        user_id=user.id
    ).count()

    discovered_count = models.Scholarship.query.count()

    scholarships = models.Scholarship.query.order_by(
        models.Scholarship.date_added.desc()
    ).limit(6).all()

    profile = models.StudentProfile.query.filter_by(
        user_id=user.id
    ).first()

    profile_fields = [
        profile.university if profile else None,
        profile.course if profile else None,
        profile.level if profile else None,
        profile.country if profile else None,
        profile.state if profile else None,
        profile.cgpa if profile else None,
        profile.interests if profile else None,
    ]

    completed_fields = sum(
        1 for field in profile_fields if field
    )

    profile_readiness = round(
        (completed_fields / len(profile_fields)) * 100
    )

    return render_template(
        "app/dashboard.html",
        user=user,
        saved_count=saved_count,
        application_count=application_count,
        discovered_count=discovered_count,
        scholarships=scholarships,
        profile_readiness=profile_readiness
    )



# --------------------------------------------------
# DISCOVER SCHOLARSHIPS
# --------------------------------------------------

@app.route("/discover")
@login_required
def discover():

    scholarships = models.Scholarship.query.order_by(
        models.Scholarship.date_added.desc()
    ).all()

    return render_template(
        "app/discover.html",
        scholarships=scholarships
    )



# --------------------------------------------------
# SAVE SCHOLARSHIP
# --------------------------------------------------

@app.route("/save/<int:scholarship_id>", methods=["POST"])
@login_required
def save_scholarship(scholarship_id):

    scholarship = db.session.get(
        models.Scholarship, scholarship_id
    )

    if not scholarship:
        return "Scholarship not found", 404

    user_id = session["user_id"]

    existing = models.SavedScholarship.query.filter_by(
        user_id=user_id,
        scholarship_id=scholarship_id
    ).first()

    if not existing:

        saved = models.SavedScholarship(
            user_id=user_id,
            scholarship_id=scholarship_id
        )

        db.session.add(saved)
        db.session.commit()

    return redirect(
        request.referrer or url_for("discover")
    )


# --------------------------------------------------
# UNSAVE SCHOLARSHIP
# --------------------------------------------------

@app.route("/unsave/<int:scholarship_id>", methods=["POST"])
@login_required
def unsave_scholarship(scholarship_id):

    saved = models.SavedScholarship.query.filter_by(
        user_id=session["user_id"],
        scholarship_id=scholarship_id
    ).first()

    if saved:
        db.session.delete(saved)
        db.session.commit()

    return redirect(
        request.referrer or url_for("saved")
    )


# --------------------------------------------------
# SAVED SCHOLARSHIPS
# --------------------------------------------------

@app.route("/saved")
@login_required
def saved():

    saved_records = models.SavedScholarship.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        models.SavedScholarship.id.desc()
    ).all()

    scholarships = [
        record.scholarship for record in saved_records
    ]

    return render_template(
        "app/saved.html",
        scholarships=scholarships
    )


# --------------------------------------------------
# TRACK APPLICATION
# --------------------------------------------------

@app.route("/track/<int:scholarship_id>", methods=["POST"])
@login_required
def track_application(scholarship_id):

    scholarship = db.session.get(
        models.Scholarship, scholarship_id
    )

    if not scholarship:
        return "Scholarship not found", 404

    user_id = session["user_id"]

    existing = models.Application.query.filter_by(
        user_id=user_id,
        scholarship_id=scholarship_id
    ).first()

    if not existing:

        application = models.Application(
            user_id=user_id,
            scholarship_id=scholarship_id,
            status="Not Started",
            notes=""
        )

        db.session.add(application)
        db.session.commit()

    return redirect(
        url_for(
            "scholarship_details",
            scholarship_id=scholarship_id
        )
    )


# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

@app.route("/applications")
@login_required
def applications():

    applications = models.Application.query.filter_by(
        user_id=session["user_id"]
    ).order_by(
        models.Application.id.desc()
    ).all()

    return render_template(
        "app/applications.html",
        applications=applications
    )


# --------------------------------------------------
# STUDENT PROFILE
# --------------------------------------------------


@app.route("/profile", methods=["GET", "POST"])
@login_required
@limiter.limit("5 per minute", methods=["POST"])
def profile():

    user = get_current_user()

    # Verify that the account still exists
    if user is None:
        session.clear()
        flash("Your account could not be verified. Please sign in again.", "error")
        return redirect(url_for("signin"))

    # Find this user's existing profile
    student_profile = models.StudentProfile.query.filter_by(
        user_id=user.id
    ).first()

    # Generate CSRF token for the form
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)

    if request.method == "POST":

        submitted_token = request.form.get("csrf_token", "")
        saved_token = session.get("csrf_token", "")

        # Validate the form submission
        if not saved_token or not secrets.compare_digest(
            submitted_token, saved_token
        ):
            flash("Invalid form submission. Please try again.", "error")
            return redirect(url_for("profile"))

        # Validate required fields
        university = request.form.get("university", "").strip()
        course = request.form.get("course", "").strip()
        level = request.form.get("level", "").strip()

        if not university or not course or not level:
            flash("Please complete the required academic fields.", "error")
            return redirect(url_for("profile"))

        # Validate CGPA
        cgpa_input = request.form.get("cgpa", "").strip()

        if cgpa_input:
            try:
                cgpa = float(cgpa_input)
            except ValueError:
                flash("Please enter a valid CGPA.", "error")
                return redirect(url_for("profile"))

            if not 0 <= cgpa <= 5:
                flash("CGPA must be between 0 and 5.", "error")
                return redirect(url_for("profile"))
        else:
            cgpa = None

        state = request.form.get("state", "").strip()
        country = request.form.get("country", "").strip() or "Nigeria"
        interests = request.form.get("interests", "").strip()

        # Update existing record or create a new one
        if student_profile is None:
            student_profile = models.StudentProfile(
                user_id=user.id
            )
            db.session.add(student_profile)

        student_profile.university = university
        student_profile.course = course
        student_profile.level = level
        student_profile.cgpa = cgpa
        student_profile.state = state
        student_profile.country = country
        student_profile.interests = interests

        try:
            db.session.commit()

            # Rotate token after successful save
            session["csrf_token"] = secrets.token_hex(32)

            flash("Profile saved successfully!", "success")

        except Exception:
            db.session.rollback()
            flash("Unable to save your profile. Please try again.", "error")

        return redirect(url_for("profile"))

    return render_template(
        "app/profile.html",
        user=user,
        profile=student_profile,
        csrf_token=session["csrf_token"]
    )




# --------------------------------------------------
# SCHOLARSHIP MATCHES
# --------------------------------------------------

@app.route("/matches")
@login_required
def matches():

    user = get_current_user()

    if not user:
        session.clear()
        return redirect(url_for("signin"))

    # Get the student's profile
    profile = models.StudentProfile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile:
        flash("Please complete your student profile first.", "warning")
        return redirect(url_for("profile"))

    # Get all scholarships
    scholarships = models.Scholarship.query.order_by(
        models.Scholarship.date_added.desc()
    ).all()

    results = []

    for scholarship in scholarships:

        match_result = match_scholarship(user, scholarship)

        results.append({
            "scholarship": scholarship,
            "match_score": match_result.get("match_score", 0),
            "reasons": match_result.get("reasons", []),
            "missing": match_result.get("missing", [])
        })

    # Highest matching scholarships first
    results.sort(
        key=lambda item: item["match_score"],
        reverse=True
    )

    return render_template(
        "app/matches.html",
        results=results
    )









# --------------------------------------------------
# SCHOLARSHIP PROFILE MATCH
# --------------------------------------------------

@app.route("/scholarship/<int:scholarship_id>")
@login_required
def scholarship_details(scholarship_id):

    user = get_current_user()

    if not user:
        session.clear()
        return redirect(url_for("signin"))

    scholarship = db.session.get(
        models.Scholarship,
        scholarship_id
    )

    if not scholarship:
        flash("Scholarship not found.", "error")
        return redirect(url_for("discover"))

    # Match this scholarship against the student's profile
    match_result = match_scholarship(user, scholarship)

    # Build the result in the format matches.html expects
    results = [{
        "scholarship": scholarship,
        "match_score": match_result.get("match_score", 0),
        "reasons": match_result.get("reasons", []),
        "missing": match_result.get("missing", [])
    }]

    return render_template(
        "app/matches.html",
        results=results
    )






# --------------------------------------------------
# AI SCHOLARSHIP ANALYSIS
# --------------------------------------------------

@app.route(
    "/app/scholarship/<int:scholarship_id>/analyse",
    methods=["GET", "POST"]
)
@login_required
def analyse_scholarship(scholarship_id):

    user = get_current_user()

    scholarship = db.session.get(
        models.Scholarship,
        scholarship_id
    )

    if not scholarship:

        flash("Scholarship not found.", "error")

        return redirect(url_for("discover"))

    if request.method == "POST":

        scholarship_text = f"""
        Title: {scholarship.title}

        Organization: {scholarship.organization}

        Description: {scholarship.description}

        Eligibility: {scholarship.eligibility}

        Country: {scholarship.country}

        Funding: {scholarship.funding}

        Deadline: {scholarship.deadline}

        Application Link: {scholarship.application_link}
        """

        analysis = analyse_with_ai(
            scholarship_text,
            user
        )

        return render_template(
            "app/analysis.html",
            scholarship=scholarship,
            analysis=analysis
        )

    return render_template(
        "app/analysis.html",
        scholarship=scholarship,
        analysis=None
    )

# --------------------------------------------------
# CREATE TABLES
# --------------------------------------------------

with app.app_context():
    db.create_all()


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)


