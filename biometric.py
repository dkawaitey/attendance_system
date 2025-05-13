#biometric.py
# This module handles biometric authentication using fingerprint recognition.


import fingerprint
import sqlite3
from datetime import datetime

DB_NAME = 'attendance.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def capture_fingerprint():
    try:
        sensor = fingerprint.FingerprintSensor()
        print("Place your finger on the scanner...")
        sensor.wait_for_finger()
        print("Finger detected, capturing...")
        fingerprint_template = sensor.capture_fingerprint()
        print("Fingerprint captured successfully.")
        return fingerprint_template
    except Exception as e:
        print(f"Error capturing fingerprint: {e}")
        return None

def match_fingerprint(fingerprint_template):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT bio_id, fingerprint_template FROM users WHERE fingerprint_template IS NOT NULL")
        rows = cursor.fetchall()
        
        for row in rows:
            bio_id, stored_template = row
            if fingerprint_template == stored_template:
                print(f"Fingerprint matched with user: {bio_id}")
                return bio_id

        print("No match found.")
        return None
    except Exception as e:
        print(f"Error during fingerprint matching: {e}")
        return None
    finally:
        conn.close()

def test_biometric_authentication():
    fingerprint_template = capture_fingerprint()
    if not fingerprint_template:
        print("Fingerprint capture failed.")
        return
    bio_id = match_fingerprint(fingerprint_template)
    if bio_id:
        print(f"User {bio_id} authenticated successfully.")
        return bio_id
    else:
        print("Authentication failed.")
        return None

if __name__ == "__main__":
    test_biometric_authentication()
