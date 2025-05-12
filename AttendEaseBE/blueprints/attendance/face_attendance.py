from flask import Blueprint, Response, jsonify, render_template
import cv2
import numpy as np
import face_recognition
from pymongo import MongoClient
from datetime import datetime
from globals import MONGO_URI, DB_NAME

face_attendance_bp = Blueprint("face_attendance_bp", __name__)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]
attendance_collection = db["attendance"]
timetable_collection = db["timetables"]

# ✅ Global variable to store last message
last_message = {"text": "Looking for your face... Stay in front of the camera.", "timestamp": datetime.now()}

# ✅ Load known face encodings at startup
print("Fetching registered user data...")
users = list(users_collection.find({"face_encoding": {"$exists": True}}))
known_encodings = [np.array(user["face_encoding"]) for user in users]
known_b0_numbers = [user["b0_number"] for user in users]
known_names = [user["name"] for user in users]
print(f"✅ Loaded {len(users)} registered users.")

def get_current_class_for_user(b0_number):
    """ ✅ Get the class happening right now for the user's course """
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_day_number = now.weekday()
    current_date = now.strftime("%Y-%m-%d")

    # ✅ Find the user's course
    user = users_collection.find_one({"b0_number": b0_number})
    if not user or "course" not in user:
        return None, None  

    user_course = user["course"]

    # ✅ Fetch timetable records for the given day and course
    timetable_records = list(timetable_collection.find({
        "course": user_course,
        "day_of_week": current_day_number,
        "start_date": {"$lte": current_date},
        "repeat_until": {"$gte": current_date}
    }))

    for record in timetable_records:
        if record["start_time"] <= current_time <= record["end_time"]:
            return record["module"], record["session_type"]

    return None, None  

def generate_frames():
    global last_message
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    success, frame = cap.read()
    if not success:
        last_message["text"] = "🚫 No camera detected. Please connect a webcam."
        last_message["timestamp"] = datetime.now()
        return

    while True:
        success, frame = cap.read()
        if not success:
            last_message["text"] = "⚠️ Camera disconnected during operation."
            last_message["timestamp"] = datetime.now()
            break

        img_small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(img_small)
        face_encodings = face_recognition.face_encodings(img_small, face_locations)

        recognized = False

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                recognized = True
                student_b0 = known_b0_numbers[best_match_index]
                student_name = known_names[best_match_index]

                # ✅ Get the module & session type
                module_name, session_type = get_current_class_for_user(student_b0)

                now = datetime.now()
                formatted_time = now.strftime("%H:%M - %d/%m/%Y")
                today_date = now.strftime("%Y-%m-%d")  # ✅ Today's date for filtering

                # ✅ Draw Green Rectangle Around Face
                y1, x2, y2, x1 = face_location
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Green rectangle
                cv2.putText(frame, f"{student_name} ({student_b0})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)  # ✅ Overlay name & B0 number

                if module_name is None:  
                    # ✅ If no class is available, update message but **don't record attendance**
                    last_message["text"] = f"No ongoing classes currently - {formatted_time}"
                    last_message["timestamp"] = datetime.now()
                    continue  

                # ✅ Prevent duplicate attendance for the same class on the same day
                existing_attendance = attendance_collection.find_one({
                    "b0_number": student_b0,
                    "module": module_name,
                    "session_type": session_type,
                    "attendance_time": {"$regex": f"^{today_date}"}
                })

                if not existing_attendance:
                    total_attendance = users_collection.find_one({"b0_number": student_b0}).get("total_attendance", 0) + 1

                    attendance_collection.insert_one({
                        "b0_number": student_b0,
                        "name": student_name,
                        "module": module_name,  # ✅ Store module separately
                        "session_type": session_type,  # ✅ Store class type separately
                        "attendance_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                        "total_attendance": total_attendance
                    })

                    users_collection.update_one(
                        {"b0_number": student_b0},
                        {"$set": {"total_attendance": total_attendance}}
                    )

                    last_message["text"] = f"{student_name} ({student_b0}) attended {module_name} - {session_type} at {formatted_time}"
                else:
                    last_message["text"] = f"{student_name} ({student_b0}) already marked for {module_name} - {session_type} today."

                last_message["timestamp"] = datetime.now()

        if not recognized:
            last_message["text"] = "Looking for your face... Stay in front of the camera."
            last_message["timestamp"] = datetime.now()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@face_attendance_bp.route('/camera-popup')
def camera_popup():
    """Serve the camera interface with 'Loading camera...' as the initial status"""
    return render_template('camera.html', status_message="Loading camera...")

@face_attendance_bp.route('/video_feed')
def video_feed():
    """Video feed route for the camera popup"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return Response(
            b"Camera not available.",
            status=503,
            mimetype='text/plain'
        )
    cap.release()
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@face_attendance_bp.route('/get-status')
def get_status():
    """Provides the latest attendance status for the frontend"""
    return jsonify({"message": last_message["text"]})

@face_attendance_bp.route('/api/v1.0/attendance/mark-attendance', methods=['POST'])
def mark_attendance():
    """Trigger face recognition and mark attendance automatically"""
    return jsonify({"message": "Face scanning activated"}), 200
