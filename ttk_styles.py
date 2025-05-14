from ttkthemes import ThemedTk
from tkinter import ttk, messagebox
import tkinter as tk
from database import start_class, end_class, sign_out, log_attendance, check_for_impersonation
from datetime import datetime


def start_class_gui():
    bio_id = entry_bio_id.get()
    success, message = start_class(bio_id)
    messagebox.showinfo("Start Class", message)


def end_class_gui():
    bio_id = entry_bio_id.get()
    success, message = end_class(bio_id)
    messagebox.showinfo("End Class", message)


def sign_out_gui():
    bio_id = entry_bio_id.get()
    success = sign_out(bio_id)
    if success:
        messagebox.showinfo("Signed Out", "Successfully signed out.")
    else:
        messagebox.showerror("Error", "Sign-out failed.")


def log_attendance_gui():
    bio_id = entry_bio_id.get()
    now = datetime.now()
    date_str = now.date().isoformat()
    time_str = now.isoformat()
    impersonation = check_for_impersonation(bio_id, date_str)
    logged = log_attendance(bio_id, date_str, sign_in=time_str, late=False, cheating=impersonation)
    if logged:
        messagebox.showinfo("Attendance", "Attendance logged.")
    else:
        messagebox.showerror("Error", "Attendance not logged (No active class).")


# Create themed window
root = ThemedTk(theme="breeze")  # Try 'arc', 'equilux', 'breeze', etc.
root.title("Smart Attendance System")

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

# Input label and entry
ttk.Label(main_frame, text="Bio ID:").grid(row=0, column=0, padx=10, pady=10)
entry_bio_id = ttk.Entry(main_frame, width=30)
entry_bio_id.grid(row=0, column=1, padx=10, pady=10)

# Buttons
ttk.Button(main_frame, text="Start Class", command=start_class_gui).grid(row=1, column=0, padx=10, pady=10)
ttk.Button(main_frame, text="End Class", command=end_class_gui).grid(row=1, column=1, padx=10, pady=10)
ttk.Button(main_frame, text="Log Attendance", command=log_attendance_gui).grid(row=2, column=0, padx=10, pady=10)
ttk.Button(main_frame, text="Sign Out", command=sign_out_gui).grid(row=2, column=1, padx=10, pady=10)

# Run the GUI
root.mainloop()
