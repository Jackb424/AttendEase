from flask import Blueprint, request, make_response, jsonify
import jwt, datetime, bcrypt
import globals
from decorators import jwt_required

auth_bp = Blueprint("auth_bp", __name__)
blacklist = globals.blacklist
users = globals.users

@auth_bp.route('/api/v1.0/signup', methods=['POST'])
def signup():
    data = request.json  # Accept JSON data
    b0_number = data.get("b0_number")
    password = data.get("password")
    name = data.get("name")
    email = data.get("email")

    if not b0_number or not password or not name or not email:
        return make_response(jsonify({"message": "All fields are required"}), 400)

    if users.find_one({"b0_number": b0_number}):
        return make_response(jsonify({"message": "User already exists"}), 409)

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = {
        "b0_number": b0_number,
        "name": name,
        "email": email,
        "password": hashed_password,
        "admin": False,
        "created_at": datetime.datetime.utcnow(),
        "total_attendance": 0,
        "last_attendance_time": None
    }
    users.insert_one(new_user)
    return make_response(jsonify({"message": "User created successfully"}), 201)

@auth_bp.route('/api/v1.0/login', methods=['POST'])
def login():
    data = request.json
    b0_number = data.get("b0_number")
    password = data.get("password")

    user = users.find_one({"b0_number": b0_number})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        token = jwt.encode({
            'user_id': str(user['_id']),
            'b0_number': user['b0_number'],
            'admin': user['admin'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, globals.secret_key, algorithm='HS256')

        response_data = {
            'x-access-token': token,
            'user': { 'name': user['name'] }  # ✅ Correctly formatted
        }
        print("✅ Sending Login Response:", response_data)  # ✅ Debugging Log
        return make_response(jsonify(response_data), 200)

    return make_response(jsonify({'message': 'Invalid credentials'}), 401)



@auth_bp.route('/api/v1.0/logout', methods=['GET'])
def logout():
    token = request.headers.get('x-access-token')
    blacklist.insert_one({"token": token})
    return make_response(jsonify({'message': 'Logout successful'}), 200)
