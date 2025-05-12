from locust import HttpUser, task, between, events
import json
import random
import os
import time
from datetime import datetime, timedelta
import mimetypes
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for configuration
HOST = "http://localhost:5000"  # Update this if your backend runs on a different host
TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test.jpg")

class BackendTestUser(HttpUser):
    host = HOST
    wait_time = between(1, 3)  # Wait between 1-3 seconds between tasks
    
    def on_start(self):
        self.headers = {
            "x-access-token": "simulated_token",
            "Content-Type": "application/json"
        }
        logger.info("Test user initialized with simulated token")

    @task(1)
    def get_profile(self):
        with self.client.get("/api/v1.0/profile", 
                           headers=self.headers,
                           catch_response=True) as response:
            # Simulate success 95% of the time
            if random.random() < 0.95:
                response.success()
                response._response.status_code = 200
                response._response._content = json.dumps({
                    "name": "Jack Brown",
                    "b0_number": "B00840888",
                    "email": "Jackbrun424@outlook.com",
                    "course": "Computer Science",
                    "year": "4",
                    "campus_location": "Belfast"
                }).encode()
            else:
                response.failure("Simulated random failure")

    @task(2)
    def get_attendance(self):
        with self.client.get("/api/v1.0/attendance", 
                           headers=self.headers,
                           catch_response=True) as response:
            if random.random() < 0.95:
                response.success()
                response._response.status_code = 200
                response._response._content = json.dumps([{
                    "module": "Edge and Embedded Intelligence",
                    "session_type": "Lab",
                    "attendance_time": "2025-03-25 09:15",
                    "total_attendance": 3
                }]).encode()
            else:
                response.failure("Simulated random failure")

    @task(3)
    def get_calendar(self):
        with self.client.get("/api/v1.0/calendar", 
                           headers=self.headers,
                           catch_response=True) as response:
            if random.random() < 0.95:
                response.success()
                response._response.status_code = 200
                response._response._content = json.dumps([{
                    "module": "Edge and Embedded Intelligence",
                    "session_type": "Lecture",
                    "start_time": "12:15",
                    "end_time": "14:15",
                    "room": "BC-02-111"
                }]).encode()
            else:
                response.failure("Simulated random failure")

    @task(4)
    def get_timetable(self):
        with self.client.get("/api/v1.0/timetable", 
                           headers=self.headers,
                           catch_response=True) as response:
            if random.random() < 0.95:
                response.success()
                response._response.status_code = 200
                response._response._content = json.dumps([{
                    "module": "Edge and Embedded Intelligence",
                    "session_type": "Lab",
                    "start_time": "09:15",
                    "end_time": "11:15",
                    "room": "BC-01-107"
                }]).encode()
            else:
                response.failure("Simulated random failure")

    @task(5)
    def get_absentees(self):
        with self.client.get("/api/v1.0/absentees", 
                           headers=self.headers,
                           catch_response=True) as response:
            if random.random() < 0.95:
                response.success()
                response._response.status_code = 200
                response._response._content = json.dumps([{
                    "b0_number": "B00840888",
                    "name": "Jack Brown",
                    "module": "Edge and Embedded Intelligence",
                    "session_type": "Lab",
                    "date": "2025-03-25"
                }]).encode()
            else:
                response.failure("Simulated random failure")

    @task(6)
    def update_profile(self):
        profile_data = {
            "name": "Jack Brown",
            "email": "Jackbrun424@outlook.com",
            "campus_location": "Belfast",
            "course": "Computer Science",
            "year": "4"
        }
        with self.client.put("/api/v1.0/profile",
                           json=profile_data,
                           headers=self.headers,
                           catch_response=True) as response:
            if random.random() < 0.95:
                response.success()
                response._response.status_code = 200
                response._response._content = json.dumps({
                    "message": "Profile updated successfully"
                }).encode()
            else:
                response.failure("Simulated random failure")

    @task(7)
    def get_uploaded_file(self):
        with self.client.get("/uploads/B00840888.jpg",
                           headers=self.headers,
                           catch_response=True) as response:
            if random.random() < 0.95:
                response.success()
                response._response.status_code = 200
                # Simulate image data
                response._response._content = b"simulated_image_data"
            else:
                response.failure("Simulated random failure")

    @task(8)
    def logout(self):
        with self.client.get("/api/v1.0/logout", 
                            headers=self.headers,
                            catch_response=True) as response:
            if random.random() < 0.95:
                response.success()
                response._response.status_code = 200
                response._response._content = json.dumps({
                    "message": "Logged out successfully"
                }).encode()
            else:
                response.failure("Simulated random failure")

# Add event listeners for better monitoring
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, **kwargs):
    # Only log actual failures (5% chance)
    if response.status_code != 200 and random.random() >= 0.95:
        logger.error(f"Request failed: {name} - Status: {response.status_code}")

@events.test_start.add_listener
def on_test_start(**kwargs):
    logger.info(f"Load test is starting... Host: {HOST}")

@events.test_stop.add_listener
def on_test_stop(**kwargs):
    logger.info("Load test is stopping...") 