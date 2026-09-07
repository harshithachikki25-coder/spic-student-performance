from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "spic_secret_key"


# ================= DATABASE =================

def init_db():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            department TEXT,
            year TEXT,
            semester TEXT
        )
    """)

    # Demo students
    students = [
        (
            "SPIC001",
            "Harshitha",
            "student123",
            "Computer Science Engineering",
            "2nd Year",
            "4th Semester"
        ),
        (
            "SPIC002",
            "Varshith",
            "student456",
            "Computer Science Engineering",
            "2nd Year",
            "4th Semester"
        ),
        (
            "SPIC003",
            "Kaveri",
            "student789",
            "Computer Science Engineering",
            "2nd Year",
            "4th Semester"
        )
    ]

    for student in students:

        try:

            cursor.execute("""
                INSERT INTO students
                (enrollment, name, password, department, year, semester)
                VALUES (?, ?, ?, ?, ?, ?)
            """, student)

        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()


# ================= HOME / LOGIN PAGE =================

@app.route("/")
def home():

    return render_template("index.html")


# ================= REGISTER =================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template("register.html")

    name = request.form["name"].strip()
    enrollment = request.form["enrollment"].strip().upper()
    department = request.form["department"]
    year = request.form["year"]
    semester = request.form["semester"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    # Check password
    if password != confirm_password:

        return render_template(
            "register.html",
            error="Passwords do not match."
        )

    # Check password length
    if len(password) < 6:

        return render_template(
            "register.html",
            error="Password must contain at least 6 characters."
        )

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Check enrollment already exists
    cursor.execute(
        "SELECT id FROM students WHERE enrollment = ?",
        (enrollment,)
    )

    existing_student = cursor.fetchone()

    if existing_student:

        conn.close()

        return render_template(
            "register.html",
            error="This enrollment number is already registered."
        )

    # Add new student
    cursor.execute("""
        INSERT INTO students
        (enrollment, name, password, department, year, semester)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        enrollment,
        name,
        password,
        department,
        year,
        semester
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# ================= LOGIN =================

@app.route("/login", methods=["POST"])
def login():

    enrollment = request.form["enrollment"].strip().upper()
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM students
        WHERE enrollment = ? AND password = ?
    """, (enrollment, password))

    student = cursor.fetchone()

    conn.close()

    if student:

        session["student_id"] = student[0]

        return redirect(url_for("dashboard"))

    return render_template(
        "index.html",
        error="Invalid enrollment number or password."
    )


# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:

        return redirect(url_for("home"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "dashboard.html",
        student=student
    )


# ================= ATTENDANCE =================

@app.route("/attendance")
def attendance():

    if "student_id" not in session:

        return redirect(url_for("home"))

    return render_template("attendance.html")


# ================= PERFORMANCE =================

@app.route("/performance")
def performance():

    if "student_id" not in session:

        return redirect(url_for("home"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "performance.html",
        student=student
    )


# ================= ASSIGNMENTS =================

@app.route("/assignments")
def assignments():

    if "student_id" not in session:

        return redirect(url_for("home"))

    return render_template("assignments.html")


# ================= ANALYTICS =================

@app.route("/analytics")
def analytics():

    if "student_id" not in session:

        return redirect(url_for("home"))

    return render_template("analytics.html")


# ================= PROFILE =================

@app.route("/profile")
def profile():

    if "student_id" not in session:

        return redirect(url_for("home"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (session["student_id"],)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "profile.html",
        student=student
    )


# ================= LOGOUT =================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ================= START APPLICATION =================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)