from flask import (
    Flask, request, jsonify, render_template,
    redirect, session, send_file
)
import json, os
import psycopg2
from psycopg2.extras import RealDictCursor


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ===============================
# CAREER RULE ENGINE
# ===============================
CAREER_RULES = {

    # ======================
    # ENGINEERING / TECH
    # ======================

    "Computer Science / IT": {
        "stream": ["Science"],
        "technical": 4,
        "logical": 4,
        "numerical": 3
    },

    "Mechanical / Electrical Engineering": {
        "stream": ["Science"],
        "technical": 3,
        "numerical": 4,
        "logical": 3
    },

    "Civil / Infrastructure Engineering": {
        "stream": ["Science"],
        "numerical": 4,
        "logical": 3
    },

    "Electronics / Robotics": {
        "stream": ["Science"],
        "technical": 4,
        "logical": 4
    },

    "Cybersecurity / AI / Data Science": {
        "stream": ["Science"],
        "technical": 4,
        "logical": 4,
        "numerical": 4
    },

    # ======================
    # MEDICAL
    # ======================

    "MBBS / Clinical Medicine": {
        "stream": ["Science"],
        "numerical": 4,
        "communication": 3,
        "logical": 3
    },

    "Dentistry / Allied Health": {
        "stream": ["Science"],
        "numerical": 3,
        "communication": 3
    },

    "Biotechnology / Genetics": {
        "stream": ["Science"],
        "technical": 3,
        "numerical": 3
    },

    "Nursing / Public Health": {
        "stream": ["Science"],
        "communication": 4
    },

    "Pharmacy / Pharma Research": {
        "stream": ["Science"],
        "numerical": 3,
        "technical": 3
    },

    # ======================
    # COMMERCE
    # ======================

    "Management / MBA Track": {
        "stream": ["Commerce"],
        "leadership": 4,
        "communication": 4
    },

    "Chartered Accountancy / Audit": {
        "stream": ["Commerce"],
        "numerical": 5,
        "logical": 4
    },

    "Finance / Investment Banking": {
        "stream": ["Commerce"],
        "numerical": 5,
        "logical": 4
    },

    "Entrepreneurship / Startup": {
        "stream": ["Commerce"],
        "leadership": 4,
        "creativity": 3
    },

    "Marketing / Brand Strategy": {
        "stream": ["Commerce"],
        "communication": 4,
        "creativity": 3
    },

    "Human Resource Management": {
        "stream": ["Commerce"],
        "communication": 4,
        "leadership": 3
    },

    # ======================
    # LAW / GOV
    # ======================

    "Law / Judiciary": {
        "stream": ["Arts", "Humanities", "Commerce"],
        "logical": 4,
        "communication": 4
    },

    "Civil Services / UPSC": {
        "stream": ["Arts", "Humanities", "Commerce", "Science"],
        "logical": 4,
        "leadership": 4
    },

    "Defence Services": {
        "stream": ["Arts", "Science"],
        "leadership": 4,
        "logical": 3
    },

    "Public Policy / Administration": {
        "stream": ["Arts", "Humanities"],
        "logical": 4,
        "communication": 3
    },

    # ======================
    # ARTS
    # ======================

    "Psychology / Counselling": {
        "stream": ["Arts", "Humanities"],
        "communication": 4,
        "leadership": 3
    },

    "Sociology / Social Work": {
        "stream": ["Arts", "Humanities"],
        "communication": 4
    },

    "History / Political Science": {
        "stream": ["Arts", "Humanities"],
        "logical": 3
    },

    "Journalism / Mass Communication": {
        "stream": ["Arts", "Humanities"],
        "communication": 4,
        "creativity": 3
    },

    "Teaching / Academia": {
        "stream": ["Arts", "Humanities"],
        "communication": 4,
        "logical": 3
    },

    # ======================
    # DESIGN
    # ======================

    "Fashion / Product Design": {
        "stream": ["Arts", "Humanities"],
        "creativity": 5
    },

    "Animation / Game Design": {
        "stream": ["Arts", "Science"],
        "creativity": 5,
        "technical": 3
    },

    "Architecture / Urban Design": {
        "stream": ["Science", "Arts"],
        "creativity": 4,
        "numerical": 3
    },

    "Fine Arts / Illustration": {
        "stream": ["Arts"],
        "creativity": 5
    },

    "Photography / Film Making": {
        "stream": ["Arts"],
        "creativity": 4,
        "communication": 3
    },

    # ======================
    # MEDIA
    # ======================

    "Content Creation / Influencer": {
        "stream": ["Arts", "Commerce"],
        "creativity": 4,
        "communication": 4
    },

    "Advertising / PR": {
        "stream": ["Arts", "Commerce"],
        "communication": 4,
        "creativity": 3
    },

    # ======================
    # SPORTS
    # ======================

    "Sports Science / Athlete": {
        "stream": ["Science"],
        "leadership": 3
    },

    "Sports Management": {
        "stream": ["Commerce"],
        "leadership": 4,
        "communication": 3
    },

    # ======================
    # ENVIRONMENT
    # ======================

    "Environmental Science": {
        "stream": ["Science"],
        "logical": 3,
        "numerical": 3
    },

    "Geology / Earth Sciences": {
        "stream": ["Science"],
        "numerical": 3
    }
}


# ===============================
# COURSE MATCHING
# ===============================

COURSE_RULES = {

    "BTech Computer Science": {
        "career": "Computer Science / IT",
        "stream": ["Science"],
        "technical": 4,
        "logical": 4,
        "numerical": 3,
        "exam": "JEE"
    },

    "MBBS": {
        "career": "MBBS / Clinical Medicine",
        "stream": ["Science"],
        "numerical": 4,
        "logical": 3,
        "exam": "NEET"
    },

    "BCom / CA Track": {
        "career": "Chartered Accountancy / Audit",
        "stream": ["Commerce"],
        "numerical": 5,
        "logical": 4,
        "exam": "CA"
    },

    "BBA": {
        "career": "Management / MBA Track",
        "stream": ["Commerce"],
        "communication": 4,
        "leadership": 3,
        "exam": "IPMAT"
    },

    "BA LLB / BBA LLB": {
        "career": "Law / Judiciary",
        "stream": ["Arts", "Commerce"],
        "logical": 4,
        "exam": "CLAT"
    },

    "BA Psychology": {
        "career": "Psychology / Counselling",
        "stream": ["Arts"],
        "communication": 4,
        "exam": "CUET"
    },

    "BDes": {
        "career": "Fashion / Product Design",
        "stream": ["Arts"],
        "creativity": 5,
        "exam": "NIFT"
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

DEFAULT_EXAMS = {
    "Science": "JEE",
    "Commerce": "IPMAT",
    "Arts": "CUET",
    "Humanities": "CUET"
}
# ===============================
# DATABASE SETUP
# ===============================

def get_db():
    return psycopg2.connect(os.environ["SUPABASE_DB_URL"],sslmode="require")



def init_db():
    con = get_db()
    cur = con.cursor()

    # ---------------------------
    # STUDENT RESPONSES
    # ---------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS responses(
        id SERIAL PRIMARY KEY,
        name TEXT,
        class_name TEXT,
        stream TEXT,
        psychometric JSONB,
        recommendations JSONB,
        exam TEXT,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ---------------------------
    # TEACHERS
    # ---------------------------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS teachers(
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    );
    """)

    con.commit()
    con.close()



init_db()

# ===============================
# CORE ENGINES
# ===============================

def compute_recommendations(scores, stream):

    ranked = []

    for career, rules in CAREER_RULES.items():

        # ---------- STREAM FILTER ----------
        if stream and stream not in rules.get("stream", []):
            continue

        score = 0

        for k, v in rules.items():
            if k == "stream":
                continue

            if scores.get(k, 0) >= v:
                score += 1

        ranked.append((career, score))

    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked[:6]


def compute_courses(scores, exams=None, stream=None):

    if isinstance(exams, str):
        exams = [e.strip().upper() for e in exams.split(",")]

    ranked = []
    detected_exams = set()

    for course, rules in COURSE_RULES.items():

        if stream and stream not in rules.get("stream", []):
            continue

        course_exam = rules.get("exam")

        if exams and course_exam and course_exam not in exams:
            continue

        score = 0

        for k, v in rules.items():
            if k in ["career", "stream", "exam"]:
                continue

            if scores.get(k, 0) >= v:
                score += 1

        ranked.append((course, score))

        if course_exam:
            detected_exams.add(course_exam)

    ranked.sort(key=lambda x: x[1], reverse=True)

    return ranked[:6], sorted(detected_exams)




def estimate_cutoff(scores, exam):

    avg = sum(scores.values()) / max(len(scores), 1)


    exam = (exam or "").upper()

    # -------------------------
    # ENGINEERING
    # -------------------------
    if exam == "JEE":
        # Percentile estimate
        val = 55 + avg * 9
        return min(99.9, round(val, 1))

    # -------------------------
    # MEDICAL
    # -------------------------
    if exam == "NEET":
        # Marks out of 720
        val = 220 + avg * 45
        return min(720, round(val))

    # -------------------------
    # CENTRAL UNIVERSITIES
    # -------------------------
    if exam == "CUET":
        # Percentile style
        val = 50 + avg * 8
        return min(99.5, round(val, 1))

    # -------------------------
    # MANAGEMENT
    # -------------------------
    if exam == "IPMAT":
        # Score approx /400
        val = 120 + avg * 22
        return min(400, round(val))

    # -------------------------
    # CA FOUNDATION
    # -------------------------
    if exam == "CA":
        # Marks /400
        val = 140 + avg * 20
        return min(400, round(val))

    # -------------------------
    # LAW
    # -------------------------
    if exam == "CLAT":
        # Score /150
        val = 60 + avg * 12
        return min(150, round(val))

    # -------------------------
    # DESIGN
    # -------------------------
    if exam in ["NIFT", "NATA"]:
        val = 70 + avg * 15
        return min(200, round(val))

    return None


def ai_summary(student, scores, careers, courses, exam=None):

    name = student[1]
    stream = student[3]

    ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    strengths = [k.replace("_"," ").title() for k,_ in ordered[:3]]
    gaps = [k.replace("_"," ").title() for k,_ in ordered[-2:]]

    top_careers = ", ".join([c[0] for c in careers[:2]])
    top_courses = ", ".join([c[0] for c in courses[:2]])

    exam_line = ""
    if exam:
        exam_line = (
            f"The recommended primary entrance pathway at this stage is {exam}. "
            "Structured preparation with regular mock testing is advised."
        )

    return f"""
{name} from the {stream} stream demonstrates pronounced aptitude in {', '.join(strengths)}.

Based on the psychometric profile, career domains such as {top_careers} appear well aligned. Corresponding undergraduate programmes including {top_courses} merit serious consideration.

Relative improvement is recommended in {', '.join(gaps)}. Targeted mentoring, concept reinforcement and assessment-driven preparation may substantially enhance readiness for competitive admissions.

{exam_line}

Overall, the student shows promising academic potential when guided through a structured, data-driven counselling and preparation framework.
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

    

    stream = data.get("Stream Opted in Class 12", "")
    exam = data.get("Competitive Exam") or DEFAULT_EXAMS.get(stream, "CUET")


    top5 = compute_recommendations(scores, stream)

    con = get_db()
    cur = con.cursor()

    cur.execute("""
INSERT INTO responses
(name,class_name,stream,exam,psychometric,recommendations)
VALUES (%s,%s,%s,%s,%s,%s)
""",(
    data.get("Full Name of Student",""),
    data.get("Class",""),
    stream,
    exam,
    json.dumps(scores),
    json.dumps(top5)
    ))

    con.commit()
    cur.close()
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
        cur = con.cursor()

        cur.execute("SELECT * FROM teachers WHERE username=%s AND password=%s",(u,p))

        row = cur.fetchone()

        cur.close()
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
    cur = con.cursor()
    cur.execute("""SELECT id,name,class_name,stream,exam,created FROM responses ORDER BY created DESC""")

    rows = cur.fetchall()
    cur.close()
    con.close()


    

    return render_template("dashboard.html", rows=rows)


# ===============================
# STUDENT DETAIL + COLLEGES
# ===============================

@app.route("/student/<int:sid>", methods=["GET","POST"])
def student_detail(sid):

    if "teacher" not in session:
        return redirect("/")

    con = get_db()
    cur = con.cursor()

    cur.execute("SELECT * FROM responses WHERE id=%s",(sid,))
    row = cur.fetchone()

    cur.close()
    con.close()

    if not row:
        return "Student not found", 404
    

    state = request.form.get("state")
    stream = row[3]



    stored_exam = row[6]

    exam = request.form.get("exam",stored_exam or DEFAULT_EXAMS.get(stream, "CUET"))



    
    scores = json.loads(row[4])
    careers = json.loads(row[5])

    courses, detected_exams = compute_courses(scores, exam, row[3])

    cutoff = estimate_cutoff(scores, exam)

    college_results = {}

    if state and state != "":
        for c,_ in careers:
            college_results[c] = INDIAN_COLLEGES.get(c,{}).get(state,[])

    summary = ai_summary(row, scores, careers, courses, exam)


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
    cur = con.cursor()
    cur.execute("SELECT * FROM responses WHERE id=%s",(sid,))
    row = cur.fetchone()
    cur.close()
    con.close()


    scores = json.loads(row[4])
    careers = json.loads(row[5])
    stream = row[3]

    exam = row[6]


    courses, _ = compute_courses(scores, exam, stream)

    summary = ai_summary(row, scores, careers, courses, exam)



    fname = f"report_{sid}.pdf"
    path = os.path.join(DATA_DIR,fname)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path,pagesize=A4)

    story=[]

    story.append(Paragraph("Career Counselling Report",styles["Title"]))
    story.append(Spacer(1,20))

    story.append(Paragraph(f"<b>Name:</b> {row[1]}",styles["Normal"]))
    story.append(Paragraph(f"<b>Class:</b> {row[2]}",styles["Normal"]))
    story.append(Paragraph(f"<b>Entrance Exam(s):</b> {exam}", styles["Normal"]))


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
    cur = con.cursor()
    cur.execute("DELETE FROM responses WHERE id=%s",(sid,))
    con.commit()
    cur.close()
    con.close()

    

    return redirect("/dashboard")


@app.route("/logout")
def logout():
    session.pop("teacher",None)
    return redirect("/")

@app.route("/__create_admin")
def create_admin():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM teachers WHERE username=%s",("admin",))
    if cur.fetchone():
        cur.close()
        con.close()
        return "Admin already exists"
    cur.execute("""INSERT INTO teachers(username,password) VALUES(%s,%s)""",("admin","admin123"))
    con.commit()
    cur.close()
    con.close() 
    return "Admin created successfully"

# ===============================
# RUN
# ===============================

if __name__ == "__main__":
    app.run(debug=True)





