import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import sqlite3

# Function to create the database connection
def get_connection():
    return sqlite3.connect('attendance.db')

# Function to handle user sign-in
def sign_in():
    user_id = user_id_entry.get()
    password = password_entry.get()

    # Sample check for demonstration. Replace with actual user validation.
    if user_id == "admin" and password == "password":
        messagebox.showinfo("Success", "Sign-in successful")
    else:
        messagebox.showerror("Error", "Invalid user ID or password")

# Function to log attendance
def log_attendance():
    bio_id = bio_id_entry.get()
    sign_in_time = datetime.now().isoformat()
    class_date = class_date_entry.get()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM attendance WHERE bio_id = ? AND class_date = ?", (bio_id, class_date))
    record = cursor.fetchone()

    if record:
        cursor.execute("UPDATE attendance SET sign_in_time = ? WHERE bio_id = ? AND class_date = ?", (sign_in_time, bio_id, class_date))
    else:
        cursor.execute("INSERT INTO attendance (bio_id, class_date, sign_in_time) VALUES (?, ?, ?)", (bio_id, class_date, sign_in_time))

    conn.commit()
    conn.close()
    messagebox.showinfo("Attendance", "Attendance logged successfully")

# Function to start a class session
def start_class():
    start_time = datetime.now().isoformat()
    class_session_label.config(text=f"Class started at {start_time}")

# Set up the main window
root = tk.Tk()
root.title("Attendance System")
root.geometry("600x400")

# Define the style
style = ttk.Style()
style.configure("TButton",
                font=("Helvetica", 12),
                padding=10,
                width=20)
style.configure("TLabel",
                font=("Helvetica", 12))
style.configure("TEntry",
                font=("Helvetica", 12),
                padding=5)

# Add Widgets
header_frame = ttk.Frame(root, padding=20)
header_frame.pack(fill='x')

header_label = ttk.Label(header_frame, text="Attendance System", font=("Helvetica", 18, "bold"))
header_label.pack()

# Sign-In Section
sign_in_frame = ttk.Frame(root, padding=20)
sign_in_frame.pack(fill='x')

user_id_label = ttk.Label(sign_in_frame, text="User ID:")
user_id_label.grid(row=0, column=0, padx=10, pady=5)
user_id_entry = ttk.Entry(sign_in_frame)
user_id_entry.grid(row=0, column=1, padx=10, pady=5)

password_label = ttk.Label(sign_in_frame, text="Password:")
password_label.grid(row=1, column=0, padx=10, pady=5)
password_entry = ttk.Entry(sign_in_frame, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=5)

sign_in_button = ttk.Button(sign_in_frame, text="Sign In", command=sign_in)
sign_in_button.grid(row=2, column=0, columnspan=2, pady=20)

# Attendance Section
attendance_frame = ttk.Frame(root, padding=20)
attendance_frame.pack(fill='x')

bio_id_label = ttk.Label(attendance_frame, text="Bio ID:")
bio_id_label.grid(row=0, column=0, padx=10, pady=5)
bio_id_entry = ttk.Entry(attendance_frame)
bio_id_entry.grid(row=0, column=1, padx=10, pady=5)

class_date_label = ttk.Label(attendance_frame, text="Class Date:")
class_date_label.grid(row=1, column=0, padx=10, pady=5)
class_date_entry = ttk.Entry(attendance_frame)
class_date_entry.grid(row=1, column=1, padx=10, pady=5)

log_attendance_button = ttk.Button(attendance_frame, text="Log Attendance", command=log_attendance)
log_attendance_button.grid(row=2, column=0, columnspan=2, pady=20)

# Start Class Section
class_session_frame = ttk.Frame(root, padding=20)
class_session_frame.pack(fill='x')

start_class_button = ttk.Button(class_session_frame, text="Start Class", command=start_class)
start_class_button.pack()

class_session_label = ttk.Label(class_session_frame, text="No class session started.")
class_session_label.pack(pady=5)

# Run the main loop
root.mainloop()
