import sqlite3
from datetime import datetime

DB_NAME = 'attendance.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        bio_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT CHECK(role IN ('student', 'lecturer', 'class_rep')) NOT NULL,
        fingerprint_template BLOB
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bio_id TEXT,
        class_date TEXT,
        sign_in_time TEXT,
        sign_out_time TEXT,
        late INTEGER,
        cheating_flag INTEGER,
        FOREIGN KEY(bio_id) REFERENCES users(bio_id)
    )''')

    cur.execute(''' 
    CREATE TABLE IF NOT EXISTS class_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        started_by TEXT,
        start_time TEXT,
        end_time TEXT,
        duration TEXT,
        is_active INTEGER
    )
    ''')

    conn.commit()
    conn.close()

def add_user(bio_id, name, role, fingerprint_template=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (bio_id, name, role, fingerprint_template) VALUES (?, ?, ?, ?)",
                (bio_id, name, role, fingerprint_template))
    conn.commit()
    conn.close()

def get_user(bio_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE bio_id = ?", (bio_id,))
    user = cur.fetchone()
    conn.close()
    return user

def get_all_fingerprints():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT bio_id, fingerprint_template FROM users WHERE fingerprint_template IS NOT NULL")
    rows = cur.fetchall()
    conn.close()
    return rows

def log_attendance(bio_id, class_date, sign_in=None, sign_out=None, late=False, cheating=False):
    conn = get_connection()
    cur = conn.cursor()

    # Ensure a class is active
    cur.execute("SELECT * FROM class_sessions WHERE is_active = 1")
    if not cur.fetchone():
        conn.close()
        return False  # No class active, block logging attendance

    cur.execute("SELECT id FROM attendance WHERE bio_id = ? AND class_date = ?", (bio_id, class_date))
    record = cur.fetchone()

    if record:
        cur.execute('''UPDATE attendance SET sign_out_time = ?, cheating_flag = ? 
                       WHERE id = ?''', (sign_out, int(cheating), record[0]))
    else:
        cur.execute('''INSERT INTO attendance (bio_id, class_date, sign_in_time, sign_out_time, late, cheating_flag)
                       VALUES (?, ?, ?, ?, ?, ?)''', (bio_id, class_date, sign_in, sign_out, int(late), int(cheating)))

    conn.commit()
    conn.close()
    return True

def check_for_impersonation(bio_id, class_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''SELECT sign_in_time, sign_out_time FROM attendance 
                   WHERE bio_id = ? AND class_date = ?''', (bio_id, class_date))
    rows = cur.fetchall()
    conn.close()

    flagged = False
    for row in rows:
        sign_in, sign_out = row
        if sign_in and sign_out:
            dt_in = datetime.fromisoformat(sign_in)
            dt_out = datetime.fromisoformat(sign_out)
            delta = (dt_out - dt_in).total_seconds() / 60
            if delta < 5:
                flagged = True
    if len(rows) > 2:
        flagged = True

    return flagged

def start_class(bio_id):
    user = get_user(bio_id)
    if user and user[2] in ('lecturer', 'class_rep'):
        conn = get_connection()
        cur = conn.cursor()

        # End any existing active class before starting new one
        cur.execute("UPDATE class_sessions SET is_active = 0 WHERE is_active = 1")

        now = datetime.now()
        class_date = now.date().isoformat()

        # Start a new class session
        cur.execute('''
            INSERT INTO class_sessions (started_by, start_time, is_active)
            VALUES (?, ?, 1)
        ''', (bio_id, now.isoformat()))

        # Log attendance for the user starting the class
        cur.execute('''
            INSERT INTO attendance (bio_id, class_date, sign_in_time, late, cheating_flag)
            VALUES (?, ?, ?, 0, 0)
        ''', (bio_id, class_date, now.isoformat()))

        conn.commit()
        conn.close()
        return True, f"Class started by {user[1]} at {now.strftime('%Y-%m-%d %H:%M:%S')}. {user[1]} also signed in automatically."

    return False, "Permission denied. Only class reps or lecturers can start a class."

def end_class(bio_id):
    user = get_user(bio_id)
    if user and user[2] == 'lecturer':
        conn = get_connection()
        cur = conn.cursor()

        # Get the latest active class
        cur.execute("SELECT id, start_time FROM class_sessions WHERE is_active = 1 ORDER BY start_time DESC LIMIT 1")
        session = cur.fetchone()

        if session:
            session_id, start_time = session
            end_time = datetime.now()
            duration = end_time - datetime.fromisoformat(start_time)

            # End the current class
            cur.execute(''' 
                UPDATE class_sessions 
                SET end_time = ?, duration = ?, is_active = 0 
                WHERE id = ? 
            ''', (end_time.isoformat(), str(duration), session_id))
            conn.commit()
            conn.close()

            return True, f"Class ended by {user[1]} at {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            conn.close()
            return False, "No active class to end."

    return False, "Only lecturers can end a class."

def sign_out(bio_id):
    user = get_user(bio_id)
    if user:
        conn = get_connection()
        cur = conn.cursor()

        now = datetime.now().isoformat()
        class_date = datetime.now().date().isoformat()
        cur.execute("SELECT id FROM attendance WHERE bio_id = ? AND class_date = ?", (bio_id, class_date))
        record = cur.fetchone()

        if record:
            cur.execute("UPDATE attendance SET sign_out_time = ? WHERE id = ?", (now, record[0]))
            conn.commit()
        conn.close()
        return True
    return False

