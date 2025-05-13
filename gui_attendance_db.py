#gui_attendance_db.py
# Biometric Attendance System with GUI


import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
from database import init_db, get_user, log_attendance, add_user

# Initialize DB
init_db()

# State
session_started = False
session_ended = False
class_start_time = None
class_end_time = None
exam_mode = False

def biometric_scan_gui():
    return simpledialog.askstring("Biometric Scan", "Enter Biometric ID:")

def is_late(current_time, start_time, limit=5):
    return (current_time - start_time).total_seconds() > limit * 60

def is_exam_late(current_time, start_time):
    return (current_time - start_time).total_seconds() > 15 * 60

def start_class():
    global session_started, class_start_time, exam_mode

    if session_started:
        messagebox.showinfo("Info", "Class already started.")
        return

    bio_id = biometric_scan_gui()
    user = get_user(bio_id)
    if not user or user[2] not in ['lecturer', 'class_rep']:
        messagebox.showerror("Access Denied", "Only lecturers or class reps can start the class.")
        return

    class_start_time = datetime.now()
    session_started = True

    exam = messagebox.askyesno("Exam Mode", "Enable Exam Mode?")
    if exam:
        exam_mode = True

    messagebox.showinfo("Class Started", f"Class started at {class_start_time.strftime('%H:%M:%S')}")

def end_class():
    global session_ended, class_end_time

    if not session_started:
        messagebox.showerror("Error", "Class hasn't started yet.")
        return

    if session_ended:
        messagebox.showinfo("Info", "Class already ended.")
        return

    bio_id = biometric_scan_gui()
    user = get_user(bio_id)
    if not user or user[2] != 'lecturer':
        messagebox.showerror("Access Denied", "Only lecturers can end the class.")
        return

    class_end_time = datetime.now()
    session_ended = True
    messagebox.showinfo("Class Ended", f"Class ended at {class_end_time.strftime('%H:%M:%S')}")

def scan_sign_in():
    if not session_started:
        messagebox.showwarning("Session Not Started", "Start the class before signing in.")
        return

    bio_id = biometric_scan_gui()
    user = get_user(bio_id)
    if not user:
        messagebox.showerror("Error", "User not found.")
        return

    current_time = datetime.now()
    date_str = class_start_time.date().isoformat()
    name = user[1]
    late = is_late(current_time, class_start_time)
    cheating = False

    if exam_mode and is_exam_late(current_time, class_start_time):
        messagebox.showwarning("Exam Security", "Late entry not allowed in exam mode.")
        return

    log_attendance(bio_id, date_str, sign_in=current_time.isoformat(), late=late, cheating=cheating)

    if late:
        messagebox.showinfo("Late", f"{name} signed in late.")
    else:
        messagebox.showinfo("Signed In", f"{name} signed in.")

def scan_sign_out():
    if not session_started:
        messagebox.showwarning("Session Not Started", "Start the class before signing out.")
        return

    bio_id = biometric_scan_gui()
    user = get_user(bio_id)
    if not user:
        messagebox.showerror("Error", "User not found.")
        return

    current_time = datetime.now()
    date_str = class_start_time.date().isoformat()
    name = user[1]
    cheating = False

    log_attendance(bio_id, date_str, sign_out=current_time.isoformat(), cheating=cheating)
    messagebox.showinfo("Signed Out", f"{name} signed out.")

# GUI
root = tk.Tk()
root.title("Biometric Attendance System")

tk.Label(root, text="Biometric Attendance System", font=("Helvetica", 16)).pack(pady=10)

btn_start = tk.Button(root, text="Start Class", width=25, command=start_class)
btn_start.pack(pady=5)
