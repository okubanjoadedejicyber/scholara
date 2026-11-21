from app import db


# Student account
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    profile = db.relationship(
        "StudentProfile",
        backref="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


# Academic profile
class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    university = db.Column(db.String(200))
    course = db.Column(db.String(200))
    level = db.Column(db.String(50))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100), default="Nigeria")
    cgpa = db.Column(db.Float)
    interests = db.Column(db.Text)


# Scholarship opportunities
class Scholarship(db.Model):
    __tablename__ = "scholarships"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    organization = db.Column(db.String(250))
    description = db.Column(db.Text)
    eligibility = db.Column(db.Text)
    country = db.Column(db.String(100))
    funding = db.Column(db.String(100))
    deadline = db.Column(db.String(100))
    application_link = db.Column(db.Text, unique=True)
    source = db.Column(db.String(250))
    date_added = db.Column(db.DateTime, default=db.func.now())


# Saved scholarships
class SavedScholarship(db.Model):
    __tablename__ = "saved_scholarships"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    scholarship_id = db.Column(
        db.Integer,
        db.ForeignKey("scholarships.id"),
        nullable=False
    )

    user = db.relationship("User", backref="saved_scholarships")
    scholarship = db.relationship("Scholarship", backref="saved_by")

    __table_args__ = (
        db.UniqueConstraint("user_id", "scholarship_id"),
    )


# Application tracking
class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    scholarship_id = db.Column(
        db.Integer,
        db.ForeignKey("scholarships.id"),
        nullable=False
    )

    status = db.Column(db.String(50), default="Not Started")
    notes = db.Column(db.Text)
    date_updated = db.Column(db.DateTime, default=db.func.now())

    user = db.relationship("User", backref="applications")
    scholarship = db.relationship("Scholarship", backref="applications")

    __table_args__ = (
        db.UniqueConstraint("user_id", "scholarship_id"),
    )