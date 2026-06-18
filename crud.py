import os
import re
import sqlite3

#Configuration 

DB_PATH = os.environ.get("DB_PATH", "leangains.db") # find db_path, if don't have it then use leangains.db as default

class DatabaseError(Exception):  # when there is a problem with the database, this error will be raised 
    pass


def get_conn():  

    try:    #try connection 
        conn = sqlite3.connect(DB_PATH)  #
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as error: 
        raise DatabaseError(
            "Cannot open the database file. Check the DB_PATH and folder permissions."
        ) from error # tells the error was caused by this original error 


# ── Input Validation ────────────────────────────────────────────
# A simple email check: some non-space chars + @ + domain + . + ending.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# A loose phone check: digits, spaces, +, -, and brackets, 7-20 chars long.
_PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")


def validate_user_input(name, email, phone):
    if not name or not name.strip():   # when name is empty or only contains whitespace
        raise ValueError("Name can't be empty.")# raise stop the program and show the error message
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
        conn.execute(            #create a table with column, type ,rule ,if not exist, if exist then do nothing
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
    with get_conn() as conn:#connect to the database,and disconnect when done automatically
        cur = conn.execute(
            "INSERT INTO users (name, email, phone) VALUES (?, ?, ?)",# get the values of name, email, phone and insert them into the users table
            (name.strip(), email.strip(), phone.strip()),
        )
        conn.commit()
        return get_user(cur.lastrowid)# return the newly created row as a dict, using the last inserted row id
 
 
#READ 
def list_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        result = []                  # empty list
        for r in rows:               # loop rows
            result.append(dict(r))   # change each row to dict and append to list
        return result                # return  list 
 
 
def get_user(uid):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        if row:               # condition to check if row is not None
            return dict(row)  # when there is a row, return it as a dict
        else:
            return None       # when it is empty, return None

 
 
#UPDATE
def update_user(uid, name, email, phone):
    validate_user_input(name, email, phone) #validate the input before updating the user
    with get_conn() as conn: #connect to the database,and disconnect when done automatically
        cur = conn.execute(
            "UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?",
            (name.strip(), email.strip(), phone.strip(), uid),
        )# change all the values of the row with the given uid to the new values
        conn.commit() #actually commit the changes to the database
        if cur.rowcount == 0: # if no rows were updated
            return None
        return get_user(uid) #return the updated row as a dict
 
 
#DELETE
def delete_user(uid):  
    with get_conn() as conn: #connect to the database,and disconnect when done automatically
        row = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()  #get the row with the given uid
        if row is None: # if there is no row with the given uid
            return None # return none
        conn.execute("DELETE FROM users WHERE id = ?", (uid,)) #delete the row with the given uid
        conn.commit() #actually commit the changes to the database
        return dict(row) 