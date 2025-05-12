from pymongo import MongoClient
import os

# 🔐 Secret Key for JWT Authentication (⚠️ Use a secure env variable in production)
secret_key = 'mysecret'  # Consider using `os.getenv('SECRET_KEY')` instead!

# ✅ MongoDB Connection
MONGO_URI = "mongodb://127.0.0.1:27017"  # Ensure MongoDB is running locally
client = MongoClient(MONGO_URI)

# ✅ Define Database
DB_NAME = "attendance_system"  # Adjust the name if needed
db = client[DB_NAME]

# ✅ Collections (Ensure consistency across your application)
users = db.users           # Stores user signup data
students = db.students     # Stores student profile details
attendance = db.attendance # Stores attendance records
blacklist = db.blacklist   # Stores invalidated JWT tokens
timetables = db.timetables # Stores timetable data
audit_logs = db.audit_logs
absentees = db.absentees


# ✅ Uploads Folder (For Profile Images & Other Uploads)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure directory exists
