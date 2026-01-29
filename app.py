from flask import Flask, request, jsonify, render_template, redirect, session
import sqlite3, json, os

app = Flask(__name__)
app.secret_key = "spark-school-secret"

# ===============================
# DATABASE PATH (Render + Local)
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.environ.get(
    "RENDER_DATA_DIR",
    os.path.join(BASE_DIR, "data")
)

os.makedirs(DATA_DIR, exist_ok=True)

DB = os.path.join(DATA_DIR, "career.db")

# ===============================
# CAREER RULE ENGINE
# ===============================

CAREER_RULES = {

    # --- STEM ---
    "Engineering": {
        "technical": 4,
        "logical": 4,
        "numerical": 3
    },

    "Data Science / AI": {
        "technical": 4,
        "numerical": 4,
        "logical": 4
    },

    "Architecture": {
        "creativity": 4,
        "technical": 3,
        "numerical": 3
    },

    "Pure Sciences / Research": {
        "logical": 4,
        "numerical": 4
    },

    # --- MEDICAL / LIFE SCI ---
    "Medical / Healthcare": {
        "numerical": 4,
        "communication": 3
    },

    "Biotechnology / Pharma": {
        "technical": 3,
        "numerical": 3
    },

    # --- BUSINESS / COMMERCE ---
    "Management / MBA Track": {
        "leadership": 4,
        "communication": 4
    },

    "Finance / Economics": {
        "numerical": 4,
        "logical": 3
    },

    "Entrepreneurship": {
        "leadership": 4,
        "creativity": 3
    },

    # --- ARTS / HUMANITIES ---
    "Law": {
        "logical": 4,
        "communication": 4
    },

    "Psychology": {
        "communication": 4,
        "leadership": 3
    },

    "Journalism / Media": {
        "communication": 4,
        "creativity": 3
    },

    "Public Policy / Civil Services": {
        "logical": 4,
        "leadership": 3
    },

    # --- DESIGN / CREATIVE ---
    "Design / Fine Arts": {
        "creativity": 4
    },

    "Animation / Game Design": {
        "creativity": 4,
        "technical": 3
    },

    # --- TECH / DIGITAL ---
    "Cybersecurity / IT": {
        "technical": 4,
        "logical": 4
    },

    "Robotics / Mechatronics": {
        "technical": 4,
        "logical": 3
    }
}

# ===============================
# DATABASE UTILS
# ===============================

def get_db():
    return sqlite3.connect(DB)


def init_db():
    con = get_db()

    con.execute("""
      CREATE TABLE IF NOT EXISTS responses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        class_name TEXT,
        stream TEXT,
        psychometric TEXT,
        recommendations TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    """)

    con.execute("""
      CREATE TABLE IF NOT EXISTS teachers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
      )
    """)

    con.commit()
    con.close()


init_db()

# ===============================
# CAREER MATCHER
# ===============================

def compute_recommendations(scores):

    ranked = []

    for career, rules in CAREER_RULES.items():
        score = 0

        for metric, cutoff in rules.items():
            if scores.get(metric, 0) >= cutoff:
                score += 1

        ranked.append((career, score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked[:5]

# ===============================
# GOOGLE FORM API
# ===============================

@app.route("/submit", methods=["POST"])
def submit():

    data = request.get_json(force=True) or {}

    def safe_int(v):
        try:
            return int(v)
        except:
            return 0

    scores = {
        "logical": safe_int(data.get("Logical Reasoning")),
        "numerical": safe_int(data.get("Numerical Ability")),
        "creativity": safe_int(data.get("Creativity")),
        "communication": safe_int(data.get("Communication Skills")),
        "leadership": safe_int(data.get("Leadership Skills")),
        "technical": safe_int(data.get("Technical Skills"))
    }

    top5 = compute_recommendations(scores)

    con = get_db()

    con.execute("""
      INSERT INTO responses
      (name,class_name,stream,psychometric,recommendations)
      VALUES(?,?,?,?,?)
    """, (
        data.get("Full Name of Student",""),
        data.get("Class",""),
        data.get("Stream Opted in Class 12",""),
        json.dumps(scores),
        json.dumps(top5)
    ))

    con.commit()
    con.close()

    return jsonify({"status": "stored"})


# ===============================
# TEACHER LOGIN
# ===============================

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        u = request.form["username"]
        p = request.form["password"]

        con = get_db()
        cur = con.execute(
            "SELECT * FROM teachers WHERE username=? AND password=?",
            (u,p)
        )

        row = cur.fetchone()
        con.close()

        if row:
            session["teacher"] = u
            return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "teacher" not in session:
        return redirect("/")

    con = get_db()

    cur = con.execute("""
      SELECT id,name,class_name,stream,created
      FROM responses
      ORDER BY created DESC
    """)

    rows = cur.fetchall()
    con.close()

    return render_template("dashboard.html", rows=rows)


@app.route("/student/<int:sid>")
def student_detail(sid):

    if "teacher" not in session:
        return redirect("/")

    con = get_db()
    cur = con.execute("SELECT * FROM responses WHERE id=?", (sid,))
    row = cur.fetchone()
    con.close()

    scores = json.loads(row[4])
    recs = json.loads(row[5])

    return render_template(
        "student_detail.html",
        student=row,
        scores=scores,
        recs=recs
    )


@app.route("/logout")
def logout():
    session.pop("teacher", None)
    return redirect("/")

@app.route("/__create_admin")
def create_admin():

    con = get_db()

    cur = con.execute(
        "SELECT * FROM teachers WHERE username=?",
        ("admin",)
    )

    if cur.fetchone():
        con.close()
        return "Admin already exists"

    con.execute("""
        INSERT INTO teachers (username,password)
        VALUES (?,?)
    """, ("admin","admin123"))

    con.commit()
    con.close()

    return "Admin created successfully"

# ===============================
# RUN LOCAL
# ===============================

if __name__ == "__main__":
    app.run(debug=True)

