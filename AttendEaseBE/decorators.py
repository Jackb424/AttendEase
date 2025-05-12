from flask import request, jsonify, make_response
import jwt
from functools import wraps
import globals

blacklist = globals.blacklist

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return make_response(jsonify({"message": "Token is missing"}), 401)
        try:
            jwt.decode(token, globals.secret_key, algorithms=["HS256"])
        except Exception:
            return make_response(jsonify({"message": "Token is invalid"}), 401)
        if blacklist.find_one({"token": token}):
            return make_response(jsonify({"message": "Token has been cancelled"}), 401)
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("x-access-token")
        try:
            data = jwt.decode(token, globals.secret_key, algorithms=["HS256"])
        except Exception:
            return make_response(jsonify({"message": "Token is invalid"}), 401)
        if data.get("admin"):
            return func(*args, **kwargs)
        else:
            return make_response(jsonify({"message": "Admin access required"}), 401)
    return wrapper
