from flask import Blueprint, request, jsonify, make_response
import jwt
import globals  # ✅ Ensure globals.py is correctly imported
from decorators import jwt_required

calendar_bp = Blueprint("calendar_bp", __name__)

# ✅ Ensure `timetables` is imported AFTER `globals.py` is properly initialized
timetables = globals.timetables
users = globals.users

@calendar_bp.route('/api/v1.0/calendar', methods=['GET'])
@jwt_required
def get_calendar():
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except Exception:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    b0_number = data.get("b0_number")

    # ✅ Fetch the user's selected course from the profile
    user = users.find_one({"b0_number": b0_number}, {"course": 1, "_id": 0})
    if not user or "course" not in user:
        return make_response(jsonify({"message": "Course not set in profile"}), 400)

    course_name = user["course"]

    # ✅ Fetch all timetable entries that match the user's selected course
    schedule = list(timetables.find({"course": course_name}))

    # ✅ Convert ObjectId to string and return the data
    for entry in schedule:
        entry["_id"] = str(entry["_id"])

    return make_response(jsonify(schedule), 200)
