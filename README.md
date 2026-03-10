🎓 Career Counselling Portal – Spark School

https://career-portal-65co.onrender.com/

A web-based career guidance system for schools where:

Students submit psychometric and academic data through a Google Form

A Flask + Python backend processes responses

Career recommendations are generated automatically

Results are stored securely in a database

Teachers log into a private dashboard to view and analyse students

Students never see recommendations directly

This project is suitable for:
✔ School deployment
✔ CBSE / ISC Computer Science projects
✔ Career counselling programs
✔ EdTech prototypes

🏗️ System Architecture
Google Form
     ↓
Google Apps Script Trigger
     ↓
Flask API (/submit)
     ↓
SQLite Database
     ↓
Teacher Dashboard (Login Protected)

📁 Project Structure
career-portal/
│
├── app.py
├── requirements.txt
├── career.db           # Auto-created on first run
├── README.md
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   └── student_detail.html
│
└── static/
    └── style.css

⚙️ Requirements

Python 3.9+

pip

GitHub account (for hosting)

Google Form

Google Apps Script

Render / PythonAnywhere account

📦 Installation (Local Testing)
git clone https://github.com/yourname/career-portal.git
cd career-portal
pip install -r requirements.txt
python app.py


Open:

http://127.0.0.1:5000

🌍 Deployment (Recommended: Render – Free Tier)

Push the project to GitHub

Create an account at https://render.com

Click New → Web Service

Connect your GitHub repo

Select the project

Build Command

pip install -r requirements.txt


Start Command

gunicorn app:app


After deployment you’ll receive:

https://your-app-name.onrender.com


Use this URL in your Google Apps Script:

https://your-app-name.onrender.com/submit

📝 Google Form Integration

Students submit responses via Google Form.

An Apps Script trigger sends data to Flask.

The function used:

onFormSubmit(e)


This runs automatically whenever a student submits the form.

👨‍🏫 Teacher Portal

Teachers can:

Login securely

View all student submissions

Click any student to see:

Psychometric scores

Career recommendations

Track counselling history

🔒 Security Notes

For production use:

Hash passwords (bcrypt)

Use HTTPS (Render provides it)

Protect API with secret token

Restrict dashboard access

Store DB backups

🚀 Future Enhancements

Admin panel for creating teachers

PDF counselling reports

Excel export

Charts & analytics

Filters by class/stream

Student comparison reports

Email result to parents

Machine-learning recommendation engine

📄 License

This project is for educational and school use.

Free to modify and extend.

🙌 Author


Developed for Spark School Career Counselling System.
