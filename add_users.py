#add_users.py
# This script adds users to the attendance system, capturing their fingerprints and storing them in the database.


import sqlite3
from biometric import capture_fingerprint  # Import biometric functions
from datetime import datetime

DB_NAME = 'attendance.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def add_user(bio_id, name, role):
    # Capture fingerprint from the user
    print(f"Capturing fingerprint for {name}...")
    fingerprint_template = capture_fingerprint()

    if fingerprint_template is None:
        print(f"Fingerprint capture failed for {name}. User not added.")
        return False

    # Store the user and fingerprint template in the database
    conn = get_connection()
    cur = conn.cursor()

    # Check if user already exists
    cur.execute("SELECT * FROM users WHERE bio_id = ?", (bio_id,))
    if cur.fetchone():
        print("User already exists!")
        conn.close()
        return False

    # Insert the user into the users table with the fingerprint data
    cur.execute("INSERT INTO users (bio_id, name, role, fingerprint_template) VALUES (?, ?, ?, ?)",
                (bio_id, name, role, fingerprint_template))
    conn.commit()
    conn.close()

    print(f"User {name} added successfully.")
    return True

from database import add_user

# Add students
add_user("S001", "Kwame Asante", "student")
add_user("S002", "Akua Mensah", "student")

# Add lecturers
add_user("L001", "Dr. Kofi Owusu", "lecturer")
add_user("L002", "Dr. Ama Serwaa", "lecturer")

# Add class reps
add_user("CR001", "Yaw Adu", "class_rep")
add_user("CR002", "Esi Baidoo", "class_rep")

print("Users added successfully.")
