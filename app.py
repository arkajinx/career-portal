from flask import (
    Flask, request, jsonify, render_template,
    redirect, session, send_file
)
import sqlite3, json, os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

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

    # ======================
    # ENGINEERING / TECH
    # ======================

    "Computer Science / IT": {
        "technical": 4,
        "logical": 4,
        "numerical": 3
    },

    "Mechanical / Electrical Engineering": {
        "technical": 3,
        "numerical": 4,
        "logical": 3
    },

    "Civil / Infrastructure Engineering": {
        "numerical": 4,
        "logical": 3
    },

    "Electronics / Robotics": {
        "technical": 4,
        "logical": 4
    },

    "Cybersecurity / AI / Data Science": {
        "technical": 4,
        "logical": 4,
        "numerical": 4
    },

    # ======================
    # MEDICAL / LIFE SCI
    # ======================

    "MBBS / Clinical Medicine": {
        "numerical": 4,
        "communication": 3,
        "logical": 3
    },

    "Dentistry / Allied Health": {
        "numerical": 3,
        "communication": 3
    },

    "Biotechnology / Genetics": {
        "technical": 3,
        "numerical": 3
    },

    "Nursing / Public Health": {
        "communication": 4
    },

    "Pharmacy / Pharma Research": {
        "numerical": 3,
        "technical": 3
    },

    # ======================
    # BUSINESS / COMMERCE
    # ======================

    "Management / MBA Track": {
        "leadership": 4,
        "communication": 4
    },

    "Chartered Accountancy / Audit": {
        "numerical": 5,
        "logical": 4
    },

    "Finance / Investment Banking": {
        "numerical": 5,
        "logical": 4
    },

    "Entrepreneurship / Startup": {
        "leadership": 4,
        "creativity": 3
    },

    "Marketing / Brand Strategy": {
        "communication": 4,
        "creativity": 3
    },

    "Human Resource Management": {
        "communication": 4,
        "leadership": 3
    },

    # ======================
    # LAW / GOVERNMENT
    # ======================

    "Law / Judiciary": {
        "logical": 4,
        "communication": 4
    },

    "Civil Services / UPSC": {
        "logical": 4,
        "leadership": 4
    },

    "Defence Services": {
        "leadership": 4,
        "logical": 3
    },

    "Public Policy / Administration": {
        "logical": 4,
        "communication": 3
    },

    # ======================
    # ARTS / HUMANITIES
    # ======================

    "Psychology / Counselling": {
        "communication": 4,
        "leadership": 3
    },

    "Sociology / Social Work": {
        "communication": 4
    },

    "History / Political Science": {
        "logical": 3
    },

    "Journalism / Mass Communication": {
        "communication": 4,
        "creativity": 3
    },

    "Teaching / Academia": {
        "communication": 4,
        "logical": 3
    },

    # ======================
    # DESIGN / CREATIVE
    # ======================

    "Fashion / Product Design": {
        "creativity": 5
    },

    "Animation / Game Design": {
        "creativity": 5,
        "technical": 3
    },

    "Architecture / Urban Design": {
        "creativity": 4,
        "numerical": 3
    },

    "Fine Arts / Illustration": {
        "creativity": 5
    },

    "Photography / Film Making": {
        "creativity": 4,
        "communication": 3
    },

    # ======================
    # MEDIA / DIGITAL
    # ======================

    "Content Creation / Influencer": {
        "creativity": 4,
        "communication": 4
    },

    "Advertising / PR": {
        "communication": 4,
        "creativity": 3
    },

    # ======================
    # SPORTS / FITNESS
    # ======================

    "Sports Science / Athlete": {
        "leadership": 3
    },

    "Sports Management": {
        "leadership": 4,
        "communication": 3
    },

    # ======================
    # ENVIRONMENT / GEO
    # ======================

    "Environmental Science": {
        "logical": 3,
        "numerical": 3
    },

    "Geology / Earth Sciences": {
        "numerical": 3
    }
}


# ===============================
# COURSE MATCHING
# ===============================

COURSE_RULES = {

    # ======================
    # ENGINEERING / TECH
    # ======================

    "BTech Computer Science": {
        "career": "Computer Science / IT",
        "technical": 4,
        "logical": 4,
        "numerical": 3,
        "jee": True
    },

    "BTech Mechanical": {
        "career": "Mechanical / Electrical Engineering",
        "technical": 3,
        "numerical": 4,
        "jee": True
    },

    "BTech Electrical": {
        "career": "Mechanical / Electrical Engineering",
        "technical": 3,
        "numerical": 4,
        "jee": True
    },

    "BTech Civil": {
        "career": "Civil / Infrastructure Engineering",
        "numerical": 4,
        "jee": True
    },

    "BTech Electronics": {
        "career": "Electronics / Robotics",
        "technical": 4,
        "logical": 4,
        "jee": True
    },

    "BTech AI / Data Science": {
        "career": "Cybersecurity / AI / Data Science",
        "technical": 4,
        "logical": 4,
        "numerical": 4,
        "jee": True
    },

    # ======================
    # MEDICAL / LIFE SCI
    # ======================

    "MBBS": {
        "career": "MBBS / Clinical Medicine",
        "numerical": 4,
        "logical": 3,
        "neet": True
    },

    "BDS (Dentistry)": {
        "career": "Dentistry / Allied Health",
        "numerical": 3,
        "neet": True
    },

    "BSc Nursing": {
        "career": "Nursing / Public Health",
        "communication": 4,
        "neet": True
    },

    "BPharm": {
        "career": "Pharmacy / Pharma Research",
        "numerical": 3,
        "technical": 3
    },

    "BSc Biotechnology": {
        "career": "Biotechnology / Genetics",
        "technical": 3,
        "numerical": 3
    },

    # ======================
    # BUSINESS / COMMERCE
    # ======================

    "BCom / CA Track": {
        "career": "Chartered Accountancy / Audit",
        "numerical": 5,
        "logical": 4
    },

    "BBA": {
        "career": "Management / MBA Track",
        "communication": 4,
        "leadership": 3
    },

    "BMS (Management Studies)": {
        "career": "Management / MBA Track",
        "leadership": 4
    },

    "BA Economics": {
        "career": "Finance / Investment Banking",
        "numerical": 5,
        "logical": 4
    },

    "Entrepreneurship Degree": {
        "career": "Entrepreneurship / Startup",
        "leadership": 4,
        "creativity": 3
    },

    # ======================
    # LAW / GOVERNMENT
    # ======================

    "BA LLB / BBA LLB": {
        "career": "Law / Judiciary",
        "logical": 4,
        "clat": True
    },

    "Integrated UPSC Track": {
        "career": "Civil Services / UPSC",
        "logical": 4,
        "leadership": 4
    },

    "Defence Studies": {
        "career": "Defence Services",
        "leadership": 4
    },

    # ======================
    # ARTS / HUMANITIES
    # ======================

    "BA Psychology": {
        "career": "Psychology / Counselling",
        "communication": 4
    },

    "BA Sociology": {
        "career": "Sociology / Social Work",
        "communication": 4
    },

    "BA Journalism": {
        "career": "Journalism / Mass Communication",
        "communication": 4,
        "creativity": 3
    },

    "BEd / Teaching": {
        "career": "Teaching / Academia",
        "communication": 4
    },

    # ======================
    # DESIGN / CREATIVE
    # ======================

    "BDes (Fashion/Product)": {
        "career": "Fashion / Product Design",
        "creativity": 5
    },

    "BArch": {
        "career": "Architecture / Urban Design",
        "creativity": 4,
        "numerical": 3,
        "nata": True
    },

    "BFA / Fine Arts": {
        "career": "Fine Arts / Illustration",
        "creativity": 5
    },

    "Animation Degree": {
        "career": "Animation / Game Design",
        "creativity": 5,
        "technical": 3
    },

    # ======================
    # MEDIA / DIGITAL
    # ======================

    "Advertising / PR Degree": {
        "career": "Advertising / PR",
        "communication": 4,
        "creativity": 3
    },

    "Content Creation Degree": {
        "career": "Content Creation / Influencer",
        "creativity": 4,
        "communication": 4
    },

    # ======================
    # SPORTS / FITNESS
    # ======================

    "BSc Sports Science": {
        "career": "Sports Science / Athlete",
        "leadership": 3
    },

    "Sports Management Degree": {
        "career": "Sports Management",
        "leadership": 4,
        "communication": 3
    },

    # ======================
    # ENVIRONMENT / GEO
    # ======================

    "BSc Environmental Science": {
        "career": "Environmental Science",
        "logical": 3,
        "numerical": 3
    },

    "BSc Geology": {
        "career": "Geology / Earth Sciences",
        "numerical": 3
    }
}


# ===============================
# STATE-WISE COLLEGES
# ===============================
INDIAN_COLLEGES = {

    # ======================
    # ENGINEERING / TECH
    # ======================

    "Computer Science / IT": {
        "West Bengal": [
            ("IIT Kharagpur", "https://www.iitkgp.ac.in"),
            ("Jadavpur University", "https://www.jaduniv.edu.in")
        ],
        "India": [
            ("IIT Bombay", "https://www.iitb.ac.in"),
            ("IIT Delhi", "https://home.iitd.ac.in"),
            ("BITS Pilani", "https://www.bits-pilani.ac.in")
        ],
        "West": [
            ("MIT (USA)", "https://www.mit.edu"),
            ("Stanford (USA)", "https://www.stanford.edu")
        ]
    },

    "Mechanical / Electrical Engineering": {
        "West Bengal": [
            ("IIT Kharagpur", "https://www.iitkgp.ac.in")
        ],
        "India": [
            ("IIT Madras", "https://www.iitm.ac.in"),
            ("IIT Roorkee", "https://www.iitr.ac.in")
        ],
        "West": [
            ("Georgia Tech (USA)", "https://www.gatech.edu")
        ]
    },

    "Cybersecurity / AI / Data Science": {
        "West Bengal": [
            ("IIT Kharagpur - CSE Dept", "https://www.iitkgp.ac.in")
        ],
        "India": [
            ("IIT Hyderabad", "https://www.iith.ac.in"),
            ("IISc Bangalore", "https://www.iisc.ac.in")
        ],
        "West": [
            ("Carnegie Mellon (USA)", "https://www.cmu.edu"),
            ("ETH Zurich (Europe)", "https://www.ethz.ch")
        ]
    },

    # ======================
    # MEDICAL / HEALTH
    # ======================

    "MBBS / Clinical Medicine": {
        "West Bengal": [
            ("Medical College, Kolkata", "https://mcc.nic.in")
        ],
        "India": [
            ("AIIMS Delhi", "https://aiims.edu"),
            ("CMC Vellore", "https://www.cmch-vellore.edu")
        ],
        "West": [
            ("Johns Hopkins (USA)", "https://www.jhu.edu")
        ]
    },

    "Dentistry / Allied Health": {
        "West Bengal": [
            ("Dr. R. Ahmed Dental College, Kolkata", "https://radckolkata.org")
        ],
        "India": [
            ("Manipal College of Dental Sciences", "https://manipal.edu")
        ],
        "West": [
            ("University of Michigan Dentistry (USA)", "https://www.umich.edu")
        ]
    },

    # ======================
    # COMMERCE / BUSINESS
    # ======================

    "Management / MBA Track": {
        "West Bengal": [
            ("IIM Calcutta", "https://www.iimcal.ac.in"),
            ("Indian Institute of Social Welfare & Business Management", "https://www.iiswa.org")
        ],
        "India": [
            ("IIM Ahmedabad", "https://www.iima.ac.in"),
            ("XLRI Jamshedpur", "https://www.xlri.ac.in")
        ],
        "West": [
            ("Harvard Business School (USA)", "https://www.hbs.edu")
        ]
    },

    "Chartered Accountancy / Audit": {
        "West Bengal": [
            ("Institute of Chartered Accountants of India – Kolkata", "https://icai.org")
        ],
        "India": [
            ("ICAI National Office", "https://icai.org")
        ],
        "West": [
            ("London School of Economics (UK)", "https://www.lse.ac.uk")
        ]
    },

    # ======================
    # LAW / GOVERNMENT
    # ======================

    "Law / Judiciary": {
        "West Bengal": [
            ("NUSRL Ranchi (accessible for WB)", "https://www.nusrlranchi.edu.in")
        ],
        "India": [
            ("NLSIU Bangalore", "https://www.nls.ac.in"),
            ("NALSAR Hyderabad", "https://www.nalsar.ac.in")
        ],
        "West": [
            ("Oxford Law (UK)", "https://www.law.ox.ac.uk")
        ]
    },

    "Civil Services / UPSC": {
        "West Bengal": [
            ("Netaji Subhas Open University (Prep in WB)", "https://www.wbnsou.ac.in")
        ],
        "India": [
            ("LBSNAA Mussoorie (Govt)", "https://www.lbsnaa.gov.in")
        ],
        "West": [
            ("USA State Department Programs (Leadership)", "https://www.state.gov")
        ]
    },

    # ======================
    # ARTS / HUMANITIES
    # ======================

    "Journalism / Mass Communication": {
        "West Bengal": [
            ("Jadavpur University – Mass Comm", "https://www.jaduniv.edu.in")
        ],
        "India": [
            ("Xavier Institute of Communications", "https://www.xic.edu"),
            ("AJK Mass Comm Research Centre", "https://www.anupamkgarg.com/ajkmcrc")
        ],
        "West": [
            ("NYU Tisch (USA)", "https://tisch.nyu.edu")
        ]
    },

    "Psychology / Counselling": {
        "West Bengal": [
            ("University of Calcutta – Psychology", "https://www.caluniv.ac.in")
        ],
        "India": [
            ("TISS Mumbai – Psychology", "https://www.tiss.edu")
        ],
        "West": [
            ("University of Toronto – Psychology (Canada)", "https://www.utoronto.ca")
        ]
    },

    # ======================
    # DESIGN / CREATIVE
    # ======================

    "Design / Fine Arts": {
        "West Bengal": [
            ("Government College of Art & Craft – Kolkata", "https://gcac.edu.in")
        ],
        "India": [
            ("NID Ahmedabad", "https://www.nid.edu"),
            ("NIFT Delhi", "https://www.nift.ac.in")
        ],
        "West": [
            ("Parsons School of Design (USA)", "https://www.newschool.edu/parsons")
        ]
    },

    "Architecture / Urban Design": {
        "West Bengal": [
            ("Jadavpur University – Architecture", "https://www.jaduniv.edu.in")
        ],
        "India": [
            ("CEPT Ahmedabad", "https://www.cept.ac.in")
        ],
        "West": [
            ("UCL Bartlett (UK)", "https://www.ucl.ac.uk/bartlett")
        ]
    }

}


# ===============================
# DATABASE SETUP
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
# CORE ENGINES
# ===============================

def compute_recommendations(scores):

    ranked = []

    for career, rules in CAREER_RULES.items():
        score = sum(
            1 for k,v in rules.items()
            if scores.get(k,0) >= v
        )

        ranked.append((career, score))

    ranked.sort(key=lambda x:x[1], reverse=True)

    return ranked[:5]


def compute_courses(scores, exam):

    ranked = []

    for course, rules in COURSE_RULES.items():

        score = 0

        if rules.get("jee") and exam == "JEE":
            score += 2

        if rules.get("neet") and exam == "NEET":
            score += 2

        for k,v in rules.items():
            if k in scores and scores[k] >= v:
                score += 1

        ranked.append((course, score))

    ranked.sort(key=lambda x:x[1], reverse=True)

    return ranked[:5]


def estimate_cutoff(scores, exam):

    avg = sum(scores.values()) / len(scores)

    if exam == "JEE":
        return round(60 + avg * 8, 1)

    if exam == "NEET":
        return round(250 + avg * 40, 1)

    return None


def ai_summary(student, scores, careers, courses):

    strengths = sorted(scores, key=scores.get, reverse=True)[:3]

    return f"""
{student[1]} demonstrates strong aptitude in {', '.join(strengths)}.

Top career tracks include {careers[0][0]} and {careers[1][0]}.

Recommended course focus: {courses[0][0]} and {courses[1][0]}.

With structured preparation the student can perform well in competitive exams.
"""

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

    exam = data.get("Competitive Exam","JEE")

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

    rows = con.execute("""
      SELECT id,name,class_name,stream,created
      FROM responses
      ORDER BY created DESC
    """).fetchall()

    con.close()

    return render_template("dashboard.html", rows=rows)


# ===============================
# STUDENT DETAIL + COLLEGES
# ===============================

@app.route("/student/<int:sid>", methods=["GET","POST"])
def student_detail(sid):

    if "teacher" not in session:
        return redirect("/")

    state = request.form.get("state")
    exam = request.form.get("exam","JEE")

    con = get_db()
    row = con.execute(
        "SELECT * FROM responses WHERE id=?", (sid,)
    ).fetchone()
    con.close()

    scores = json.loads(row[4])
    careers = json.loads(row[5])

    courses = compute_courses(scores, exam)
    cutoff = estimate_cutoff(scores, exam)

    college_results = {}

    if state:
        for c,_ in careers:
            college_results[c] = INDIAN_COLLEGES.get(c,{}).get(state,[])

    summary = ai_summary(row, scores, careers, courses)

    return render_template(
        "student_detail.html",
        student=row,
        scores=scores,
        recs=careers,
        courses=courses,
        colleges=college_results,
        cutoff=cutoff,
        summary=summary,
        selected_state=state,
        exam=exam
    )


# ===============================
# PDF EXPORT
# ===============================

@app.route("/report/<int:sid>")
def report(sid):

    if "teacher" not in session:
        return redirect("/")

    con = get_db()
    row = con.execute(
        "SELECT * FROM responses WHERE id=?", (sid,)
    ).fetchone()
    con.close()

    scores = json.loads(row[4])
    careers = json.loads(row[5])
    courses = compute_courses(scores,"JEE")

    summary = ai_summary(row,scores,careers,courses)

    fname = f"report_{sid}.pdf"
    path = os.path.join(DATA_DIR,fname)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path,pagesize=A4)

    story=[]

    story.append(Paragraph("Career Counselling Report",styles["Title"]))
    story.append(Spacer(1,20))

    story.append(Paragraph(f"<b>Name:</b> {row[1]}",styles["Normal"]))
    story.append(Paragraph(f"<b>Class:</b> {row[2]}",styles["Normal"]))

    data=[["Skill","Score"]] + [[k,v] for k,v in scores.items()]
    story.append(Table(data))

    story.append(Spacer(1,15))
    story.append(Paragraph("<b>AI Summary</b>",styles["Heading2"]))
    story.append(Paragraph(summary,styles["Normal"]))

    doc.build(story)

    return send_file(path,as_attachment=True)


# ===============================
# DELETE STUDENT
# ===============================

@app.route("/delete/<int:sid>",methods=["POST"])
def delete_student(sid):

    if "teacher" not in session:
        return redirect("/")

    con=get_db()
    con.execute("DELETE FROM responses WHERE id=?", (sid,))
    con.commit()
    con.close()

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.pop("teacher",None)
    return redirect("/")


# ===============================
# RUN
# ===============================

if __name__ == "__main__":
    app.run(debug=True)
