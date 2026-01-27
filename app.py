from flask import Flask, request, jsonify, render_template, redirect, session
import sqlite3, json, os

app = Flask(__name__)
app.secret_key = "spark-school-secret"

DB = "career.db"

CAREER_RULES = {
    "Engineering": {"technical":4,"logical":4},
    "Medical": {"numerical":4,"communication":3},
    "Management": {"leadership":4,"communication":4},
    "Design": {"creativity":4},
    "Law": {"logical":4,"communication":4}
}


def get_db():
    return sqlite3.connect(DB)


def init_db():
    con = get_db()
    con.execute("""
      CREATE TABLE IF NOT EXISTS responses(
        id INTEGER PRIMARY KEY,
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
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT
      )
    """)
    con.commit()
    con.close()

init_db()


def compute_recommendations(scores):
    ranked = []
    for career, rules in CAREER_RULES.items():
        score = sum(1 for k,v in rules.items() if scores[k] >= v)
        ranked.append((career, score))

    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked[:5]


# ---------- API FOR GOOGLE FORM ----------

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(force=True)

    scores = {
        "logical": int(data["Logical Reasoning"]),
        "numerical": int(data["Numerical Ability"]),
        "creativity": int(data["Creativity"]),
        "communication": int(data["Communication Skills"]),
        "leadership": int(data["Leadership Skills"]),
        "technical": int(data["Technical Skills"])
    }

    top5 = compute_recommendations(scores)

    con = get_db()
    con.execute("""
      INSERT INTO responses
      (name,class_name,stream,psychometric,recommendations)
      VALUES(?,?,?,?,?)
    """, (
        data["Full Name of Student"],
        data["Class"],
        data["Stream Opted in Class 12"],
        json.dumps(scores),
        json.dumps(top5)
    ))
    con.commit()
    con.close()

    return jsonify({"status": "stored"})


# ---------- TEACHER PORTAL ----------

@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        con = get_db()
        cur = con.execute("SELECT * FROM teachers WHERE username=? AND password=?", (u,p))
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
    cur = con.execute("SELECT id,name,class_name,stream,created FROM responses ORDER BY created DESC")
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

    return render_template("student_detail.html",
                           student=row,
                           scores=scores,
                           recs=recs)

@app.route("/logout")
def logout():
    session.pop("teacher", None)
    return redirect("/")

# ---------- RUN ----------

if __name__ == "__main__":
    app.run()
