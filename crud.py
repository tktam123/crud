import os
import re
import sqlite3

#Configuration 

DB_PATH = os.environ.get("DB_PATH", "leangains.db")

class DatabaseError(Exception):
    pass


def get_conn():

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        raise DatabaseError(
            "Cannot open the database file. Check the DB_PATH and folder permissions."
        ) from e


# ── Input Validation ────────────────────────────────────────────
# A simple email check: some non-space chars + @ + domain + . + ending.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# A loose phone check: digits, spaces, +, -, and brackets, 7-20 chars long.
_PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")


def validate_user_input(name, email, phone):
    if not name or not name.strip():
        raise ValueError("Name can't be empty.")
    if not email or not email.strip():
        raise ValueError("Email can't be empty.")
    if not _EMAIL_RE.match(email.strip()):
        raise ValueError(f"Email is the wrong format, should look like abc@gmail.com: {email}")
    if not phone or not phone.strip():
        raise ValueError("Phone can't be empty.")
    if not _PHONE_RE.match(phone.strip()):
        raise ValueError(f"Phone is the wrong format, use digits and + - ( ) only: {phone}")


def init_db():
    with get_conn() as conn:
        conn.execute(            
            """
            CREATE TABLE IF NOT EXISTS users (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL
            )
            """
 
        )
        conn.commit()


#CREATE
def create_user(name, email, phone):
    validate_user_input(name, email, phone)
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, phone) VALUES (?, ?, ?)",
            (name.strip(), email.strip(), phone.strip()),
        )
        conn.commit()
        return get_user(cur.lastrowid)
 
 
#READ 
def list_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        result = []                  # empty list
        for r in rows:               # loop rows
            result.append(dict(r))   # change each row to dict and append to list
        return result                # 4. return  list 
 
 
def get_user(uid):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        if row:               # condition to check if row is not None
            return dict(row)  # when there is a row, return it as a dict
        else:
            return None       # when it is empty, return None

 
 
#UPDATE
def update_user(uid, name, email, phone):
    validate_user_input(name, email, phone)
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?",
            (name.strip(), email.strip(), phone.strip(), uid),
        )
        conn.commit()
        if cur.rowcount == 0:
            return None
        return get_user(uid)
 
 
#DELETE
def delete_user(uid):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        if row is None:
            return None
        conn.execute("DELETE FROM users WHERE id = ?", (uid,))
        conn.commit()
        return row