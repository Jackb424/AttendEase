import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_mail import Mail
from blueprints.auth.auth import auth_bp
from blueprints.attendance.attendance import attendance_bp
from blueprints.profile.profile import profile_bp
from blueprints.calendar.calendar import calendar_bp
from blueprints.attendance.face_attendance import face_attendance_bp
from blueprints.timetable.timetable import timetable_bp
from blueprints.absenteeism.absenteeism import absentee_bp, send_absentee_emails_core, check_absentees
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import pytz
import globals

# ✅ Initialize Flask App
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = globals.UPLOAD_FOLDER
app.secret_key = globals.secret_key

# ✅ Mail Configuration (Set BEFORE importing Mail)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'attendease42@gmail.com'
app.config['MAIL_PASSWORD'] = 'xqvf lljk rxav piad'

# ✅ Initialize Mail
mail = Mail(app)

# ✅ Inject Mail instance into absenteeism module
from blueprints.absenteeism import absenteeism
absenteeism.mail = mail  # Set mail object globally inside absenteeism.py

# ✅ Allow CORS for Angular Frontend
CORS(app,
     resources={r"/api/v1.0/*": {"origins": "http://localhost:4200"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "x-access-token"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# ✅ Register All Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(calendar_bp)
app.register_blueprint(face_attendance_bp)
app.register_blueprint(timetable_bp)
app.register_blueprint(absentee_bp)

def send_absentee_emails():
    with app.app_context():
        return send_absentee_emails_core()

# ✅ Background Scheduler for Automated Tasks
scheduler = BackgroundScheduler(timezone=pytz.UTC)

# ✅ Schedule Email Notifications at 19:30 Daily
scheduler.add_job(
    send_absentee_emails,
    "cron",
    hour=23,
    minute=50,
    timezone=timezone("Europe/London")  # UK time, auto-adjusts for BST/GMT
)

# ✅ Schedule Absentee Checking Every 30 Minutes
scheduler.add_job(check_absentees, "interval", minutes=30)

scheduler.start()

# ✅ Serve Uploaded Profile Pictures
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ✅ Add Security Headers
@app.after_request
def add_security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "font-src 'self' https://fonts.gstatic.com; "
        "style-src 'self' https://fonts.googleapis.com; "
        "script-src 'self'; "
        "img-src 'self' data: http://localhost:5000/uploads/; "
        "connect-src 'self' http://localhost:5000;"
    )
    return response

# ✅ Run the App
if __name__ == "__main__":
    app.run(debug=True)
