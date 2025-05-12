import os
import cv2
import face_recognition
from flask import Blueprint, request, make_response, jsonify, url_for
import jwt
import datetime
import globals
from pymongo import MongoClient
from globals import MONGO_URI, DB_NAME
from decorators import jwt_required
from flask_cors import cross_origin

profile_bp = Blueprint("profile_bp", __name__)

# MongoDB Setup
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db["users"]

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # ✅ Ensure folder exists

@profile_bp.route('/api/v1.0/profile', methods=['GET']) 
@jwt_required
def get_profile():
    token = request.headers.get("x-access-token")
    try:
        data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    except Exception:
        return make_response(jsonify({"message": "Invalid token"}), 401)

    b0_number = data.get("b0_number")
    user = users_collection.find_one({"b0_number": b0_number}, {"password": 0})  

    if user:
        user["_id"] = str(user["_id"])
        user["is_admin"] = data.get("admin", False)  # ✅ Add admin flag
        return make_response(jsonify(user), 200)
    else:
        return make_response(jsonify({"message": "User not found"}), 404)

@profile_bp.route('/api/v1.0/profile', methods=['PUT'])
@cross_origin()  # ✅ Allow CORS only for this endpoint
@jwt_required
def update_profile():
    """Handles updating user profile including image encoding"""
    token = request.headers.get("x-access-token")
    data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
    b0_number = data.get("b0_number")
    
    update_data = {}

    if "course" in request.form:
        update_data["course"] = request.form.get("course")
    if "year" in request.form:
        update_data["year"] = request.form.get("year")
    if "campus_location" in request.form:
        update_data["campus_location"] = request.form.get("campus_location")

    if "face_image" in request.files:
        file = request.files["face_image"]
        filename = f"{b0_number}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process and encode face
        img = cv2.imread(filepath)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img_rgb)

        if encodings:
            face_encoding = encodings[0].tolist()
            update_data["face_encoding"] = face_encoding
            update_data["profile_image"] = url_for('uploaded_file', filename=filename, _external=True)
        else:
            return jsonify({"error": "No face detected in the image"}), 400

    if update_data:
        users_collection.update_one({"b0_number": b0_number}, {"$set": update_data}, upsert=True)

    return jsonify({"message": "Profile updated successfully"}), 200