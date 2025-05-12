from flask import Blueprint, jsonify
import datetime
from pymongo import MongoClient
from globals import MONGO_URI, DB_NAME
from flask_mail import Mail, Message

absentee_bp = Blueprint("absentee_bp", __name__)

# Database setup
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]
attendance_collection = db["attendance"]
timetable_collection = db["timetables"]
absentees_collection = db["absentees"]

# Mail instance
mail = Mail()

def check_absentees():
    """Identifies absent students and logs them into absentees collection"""
    now = datetime.datetime.utcnow()
    today_date = now.strftime("%Y-%m-%d")
    current_day = now.weekday()  # 0 = Monday

    absentees = []

    # Get all scheduled classes for today
    scheduled_classes = list(timetable_collection.find({"day_of_week": current_day}))

    for session in scheduled_classes:
        module_name = session["module"]
        session_type = session["session_type"]
        start_time = session["start_time"]
        end_time = session["end_time"]
        course = session["course"]

        # Get all students enrolled in this course
        students = list(users_collection.find({"course": course}))

        # Skip if session hasn't ended yet
        class_end_dt = datetime.datetime.strptime(f"{today_date} {end_time}", "%Y-%m-%d %H:%M")
        if now < class_end_dt:
            continue

        for student in students:
            b0_number = student.get("b0_number")
            student_name = student.get("name")
            email = student.get("email", "")

            # Check if attendance is recorded
            attendance_exists = attendance_collection.find_one({
                "b0_number": b0_number,
                "module": module_name,
                "session_type": session_type,
                "attendance_time": {"$regex": f"^{today_date}"}
            })

            # Check if absentee already logged
            already_logged = absentees_collection.find_one({
                "b0_number": b0_number,
                "module": module_name,
                "session_type": session_type,
                "date": today_date
            })

            if not attendance_exists and not already_logged:
                absentee_data = {
                    "b0_number": b0_number,
                    "name": student_name,
                    "module": module_name,
                    "session_type": session_type,
                    "start_time": start_time,
                    "end_time": end_time,
                    "date": today_date,
                    "email": email
                }

                absentees_collection.insert_one(absentee_data)
                absentees.append(absentee_data)

                # Increment absentee count in users collection
                users_collection.update_one(
                    {"b0_number": b0_number},
                    {"$inc": {"absentee_count": 1}}
                )

    return absentees


def send_absentee_emails_core():
    """Sends absentee emails (must be wrapped in app context from outside)"""
    today_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    absentees = list(absentees_collection.find({"date": today_date}))

    if not absentees:
        return "No absentees today."

    for student in absentees:
        email = student.get("email", "")
        if not email:
            continue

        msg = Message(
            subject="📌 Attendance Alert - Missed Class Notification",
            sender="admin@attendance.com",
            recipients=[email]
        )

        msg.body = f"""
Hi {student['name']},

Our records show that you missed the following class today:

📚 Module: {student['module']}
🏫 Session Type: {student['session_type']}
🕒 Time: {student['start_time']} - {student['end_time']}
📅 Date: {student['date']}

Please ensure you attend future classes and contact your lecturer if needed.

Regards,
Attendance System
"""
        mail.send(msg)

    return "Emails sent successfully."


# ========== API ROUTES ==========

@absentee_bp.route("/api/v1.0/absentees", methods=["GET"])
def get_absentees():
    """Fetch all absentees for admin dashboard"""
    absentees = list(absentees_collection.find().sort("date", -1))
    for a in absentees:
        a["_id"] = str(a["_id"])
    return jsonify(absentees)


@absentee_bp.route("/api/v1.0/test-email", methods=["GET"])
def send_test_email():
    """Send test email to verify Flask-Mail configuration"""
    try:
        test_email = "jackbrun424@outlook.com"
        msg = Message(
            subject="✅ Test Email - Attendance System",
            sender="attendease42@gmail.com",  # Must match MAIL_USERNAME
            recipients=[test_email],
            body="""
Hello 👋,

This is a test email from the Flask Attendance System.
If you received this, your Flask-Mail setup is working correctly!

Regards,
Attendance System
"""
        )
        mail.send(msg)
        return jsonify({"message": "✅ Test email sent successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@absentee_bp.route("/api/v1.0/test-absentee-email", methods=["GET"])
def trigger_absentee_email_check():
    """Manually trigger absentee email notifications (simulate cron job)"""
    result = send_absentee_emails_core()
    return jsonify({"result": result}), 200
