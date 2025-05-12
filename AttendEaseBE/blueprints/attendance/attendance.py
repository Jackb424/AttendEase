from flask import Blueprint, request, make_response, jsonify
import datetime, jwt
import globals
from decorators import jwt_required
from bson import ObjectId
from .face_attendance import mark_attendance

attendance_bp = Blueprint("attendance_bp", __name__)
users = globals.users
attendance = globals.attendance
audit_logs = globals.audit_logs
timetable = globals.timetables
absentees = globals.absentees 

MIN_ATTENDANCE_INTERVAL = 3600  # ✅ Prevent attendance spam (30 min)

@attendance_bp.route('/api/v1.0/attendance', methods=['POST'])
@jwt_required
def mark_attendance_api():
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({"message": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    b0_number = data.get("b0_number")
    user = users.find_one({"b0_number": b0_number})
    if not user:
        return make_response(jsonify({"message": "User not found"}), 404)

    now = datetime.datetime.utcnow()
    last_time_str = user.get("last_attendance_time", "2000-01-01 00:00:00")
    last_time = datetime.datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")

    elapsed = (now - last_time).total_seconds()
    if elapsed < MIN_ATTENDANCE_INTERVAL:
        return make_response(jsonify({"message": "Attendance already marked recently"}), 200)

    users.update_one({"b0_number": b0_number}, {
        "$set": {"last_attendance_time": now.strftime("%Y-%m-%d %H:%M:%S")},
        "$inc": {"total_attendance": 1}
    })
    updated_total = user.get("total_attendance", 0) + 1

    record = {
        "b0_number": b0_number,
        "attendance_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "total_attendance": updated_total
    }
    attendance.insert_one(record)
    return make_response(jsonify({"message": f"Attendance marked for {b0_number}", "record": record}), 200)


@attendance_bp.route('/api/v1.0/attendance', methods=['GET'])
@jwt_required
def get_attendance():
    """Fetch attendance records, but admins only see their own records on the My Attendance page"""
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({"message": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    b0_number = data.get("b0_number")  # ✅ Get the user's B0 number

    # ✅ Always return the logged-in user's attendance records, even if they are an admin
    records = list(attendance.find({"b0_number": b0_number}))

    # ✅ Convert ObjectId to string for frontend
    for r in records:
        r["_id"] = str(r["_id"])

    return make_response(jsonify(records), 200)


@attendance_bp.route('/api/v1.0/attendance/all', methods=['GET'])
@jwt_required
def get_all_attendance():
    """Fetch all attendance records (Admins Only)"""
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({"message": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    if not data.get("admin"):  # ✅ Ensure only admins can access this
        return make_response(jsonify({"message": "Access denied"}), 403)

    records = list(attendance.find())  # ✅ Fetch all records
    for r in records:
        r["_id"] = str(r["_id"])
    
    return make_response(jsonify(records), 200)


@attendance_bp.route('/api/v1.0/mark-attendance', methods=['POST'])
def mark_attendance_route():
    """API route to trigger face recognition for attendance"""
    try:
        result, status_code = mark_attendance()  # ✅ Call function from face_attendance.py
        return jsonify(result), status_code  # ✅ Return the response
    except Exception as e:
        return jsonify({"message": f"Error marking attendance: {str(e)}"}), 500

@attendance_bp.route('/api/v1.0/analytics', methods=['GET'])
@jwt_required
def analytics():
    total_users = users.count_documents({})
    total_attendance = attendance.count_documents({})
    analytics_data = {
        "totalUsers": total_users,
        "totalAttendance": total_attendance
    }
    return make_response(jsonify(analytics_data), 200)

# ✅ UPDATE ATTENDANCE RECORD (Admin Only)
@attendance_bp.route('/api/v1.0/attendance/update', methods=['PUT'])
@jwt_required
def update_attendance():
    """ ✅ Update attendance record & log the action """
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({"message": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    if not data.get("admin"):  
        return make_response(jsonify({"message": "Access denied"}), 403)

    # ✅ Fetch the admin's name & B0 number from the database
    admin_b0 = data.get("b0_number", "Unknown Admin B0")
    admin = users.find_one({"b0_number": admin_b0})

    if admin:
        admin_name = admin.get("name", "Unknown Admin")
    else:
        admin_name = "Unknown Admin"

    record_data = request.json
    record_id = record_data.get("_id")
    
    if not record_id:
        return make_response(jsonify({"message": "Record ID required"}), 400)

    updated_data = {
        "module": record_data["module"],
        "session_type": record_data["session_type"],
        "attendance_time": record_data["attendance_time"]
    }

    attendance.update_one({"_id": ObjectId(record_id)}, {"$set": updated_data})

    # ✅ Log the update in audit logs
    audit_logs.insert_one({
        "admin_name": admin_name,  
        "admin_b0": admin_b0,  
        "action": f"Updated attendance record for {record_data.get('b0_number', 'Unknown B0')} - {record_data.get('module', 'Unknown Module')} ({record_data.get('session_type', 'Unknown Type')})",
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    })

    return make_response(jsonify({"message": "Attendance updated successfully & logged"}), 200)


@attendance_bp.route('/api/v1.0/attendance/delete/<record_id>', methods=['DELETE'])
@jwt_required
def delete_attendance(record_id):
    """ ✅ Delete an attendance record & log the action """
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({"message": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    # ✅ Ensure user is an admin before allowing deletion
    if not data.get("admin"):  
        return make_response(jsonify({"message": "Access denied"}), 403)

    # ✅ Fetch the admin's name & B0 number from the database
    admin_b0 = data.get("b0_number", "Unknown Admin B0")
    admin = users.find_one({"b0_number": admin_b0})

    if admin:
        admin_name = admin.get("name", "Unknown Admin")
    else:
        admin_name = "Unknown Admin"

    # ✅ Get the record before deleting it
    deleted_record = attendance.find_one({"_id": ObjectId(record_id)})

    if deleted_record:
        attendance.delete_one({"_id": ObjectId(record_id)})

        # ✅ Ensure all necessary fields exist before logging
        b0_number = deleted_record.get("b0_number", "Unknown B0")
        module = deleted_record.get("module", "Unknown Module")
        session_type = deleted_record.get("session_type", "Unknown Type")

        # ✅ Log the deletion in audit logs
        audit_logs.insert_one({
            "admin_name": admin_name,  # ✅ Properly log admin's name
            "admin_b0": admin_b0,  # ✅ Log admin's B0 number
            "action": f"Deleted attendance record for {b0_number} - {module} ({session_type})",
            "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })

        return make_response(jsonify({"message": "Attendance record deleted & logged"}), 200)

    return make_response(jsonify({"message": "Record not found"}), 404)


# ✅ GET AUDIT LOGS (Admin Only)
@attendance_bp.route('/api/v1.0/attendance/audit-logs', methods=['GET'])
@jwt_required
def get_audit_logs():
    """ ✅ Fetch audit logs for admin """
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({"message": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    if not data.get("admin"):  # ✅ Only allow admins to access logs
        return make_response(jsonify({"message": "Access denied"}), 403)

    logs = list(audit_logs.find().sort("timestamp", -1))  # ✅ Fetch logs (newest first)
    for log in logs:
        log["_id"] = str(log["_id"])
    return make_response(jsonify(logs), 200)

@attendance_bp.route('/api/v1.0/attendance/check-absentees', methods=['POST'])
@jwt_required
def check_absentees():
    """
    ✅ Check for students who missed their scheduled class.
    This runs after each class session to determine absentees.
    """
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({"message": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    if not data.get("admin"):  # ✅ Ensure only admins can trigger this
        return make_response(jsonify({"message": "Access denied"}), 403)

    now = datetime.datetime.utcnow()
    current_date = now.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    current_time = now.strftime("%H:%M")  # Format: HH:MM
    current_day_number = now.weekday()  # 0 = Monday, 6 = Sunday

    print(f"📅 Checking absentees for {current_date} at {current_time}")

    # ✅ Fetch all classes that were scheduled today before current time
    scheduled_classes = list(timetable.find({
        "day_of_week": current_day_number,
        "start_date": {"$lte": current_date},
        "repeat_until": {"$gte": current_date},
        "end_time": {"$lt": current_time}  # ✅ Only check past classes
    }))

    if not scheduled_classes:
        return jsonify({"message": "No past classes to check."}), 200

    absentees_list = []

    for scheduled_class in scheduled_classes:
        module = scheduled_class["module"]
        session_type = scheduled_class["session_type"]
        course = scheduled_class["course"]
        end_time = scheduled_class["end_time"]

        # ✅ Fetch all students enrolled in this course
        students = list(users.find({"course": course}, {"b0_number": 1, "name": 1, "_id": 0}))

        for student in students:
            student_b0 = student["b0_number"]
            student_name = student["name"]

            # ✅ Check if the student has attendance recorded for this class
            attendance_record = attendance.find_one({
                "b0_number": student_b0,
                "module": module,
                "session_type": session_type,
                "attendance_time": {"$regex": f"^{current_date}"}  # ✅ Check only for today's attendance
            })

            if not attendance_record:
                print(f"🚨 {student_name} (B0: {student_b0}) MISSED {module} ({session_type}) at {end_time}")

                # ✅ Insert into absentees collection
                absentees.insert_one({
                    "b0_number": student_b0,
                    "name": student_name,
                    "module": module,
                    "session_type": session_type,
                    "missed_date": current_date,
                    "missed_time": end_time
                })

                absentees_list.append({
                    "b0_number": student_b0,
                    "name": student_name,
                    "module": module,
                    "session_type": session_type,
                    "missed_date": current_date,
                    "missed_time": end_time
                })

    return jsonify({"message": "Absentees checked", "absentees": absentees_list}), 200

@attendance_bp.route('/api/v1.0/attendance/absentees', methods=['GET'])
@jwt_required
def get_absentees():
    """
    ✅ Fetch all absentee records for the admin dashboard.
    """
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({"message": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    if not data.get("admin"):  # ✅ Only admins can access
        return make_response(jsonify({"message": "Access denied"}), 403)

    absentee_records = list(absentees.find().sort("missed_date", -1))  # ✅ Fix variable name
    for record in absentee_records:
        record["_id"] = str(record["_id"])

    return jsonify(absentee_records), 200

# DELETE absentee record and mark as attended
@attendance_bp.route('/api/v1.0/absentees/delete/<record_id>', methods=['DELETE'])
@jwt_required
def delete_absentee(record_id):
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({"message": "Token expired"}), 401)
    except jwt.InvalidTokenError:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    if not data.get("admin"):
        return make_response(jsonify({"message": "Access denied"}), 403)

    # ✅ Get correct admin info
    admin_b0 = data.get("b0_number", "Unknown Admin B0")
    admin_user = users.find_one({"b0_number": admin_b0})
    admin_name = admin_user.get("name", "Unknown Admin") if admin_user else "Unknown Admin"

    absentee_record = absentees.find_one({"_id": ObjectId(record_id)})
    if not absentee_record:
        return make_response(jsonify({"message": "Absentee record not found"}), 404)

    # Handle both old/new formats of absentee fields
    attendance_date = absentee_record.get("date") or absentee_record.get("missed_date")
    attendance_time = absentee_record.get("start_time") or absentee_record.get("missed_time")
    if not attendance_date or not attendance_time:
        return jsonify({"message": "Missing date/time fields in absentee record"}), 400

    attendance_datetime = f"{attendance_date} {attendance_time}"

    # Get the student’s details
    student_b0 = absentee_record.get("b0_number")
    student_name = absentee_record.get("name", "Unknown Student")
    student_user = users.find_one({"b0_number": student_b0})
    student_current_total = student_user.get("total_attendance", 0) if student_user else 0

    # ✅ Insert into attendance
    attendance.insert_one({
        "b0_number": student_b0,
        "name": student_name,
        "module": absentee_record["module"],
        "session_type": absentee_record["session_type"],
        "attendance_time": attendance_datetime,
        "total_attendance": student_current_total + 1
    })

    # ✅ Update student's total attendance
    users.update_one(
        {"b0_number": student_b0},
        {"$inc": {"total_attendance": 1}}
    )

    # ✅ Remove from absentees
    absentees.delete_one({"_id": ObjectId(record_id)})

    # ✅ Correctly log the action by the admin (not the student)
    audit_logs.insert_one({
        "admin_name": admin_name,
        "admin_b0": admin_b0,
        "action": f"Deleted absentee record and marked attendance for {student_b0} ({absentee_record['module']} - {absentee_record['session_type']})",
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    })

    return jsonify({"message": "Absentee removed and attendance marked"}), 200

