import os
import re
import sqlite3

#Configuration 

DB_PATH = os.environ.get("DB_PATH", "leangains.db") # find db_path, if don't have it then use leangains.db as default

class DatabaseError(Exception):  # when there is a problem with the database, this error will be raised 
    pass


def get_conn():  

    try:    #try connection 
        conn = sqlite3.connect(DB_PATH)  
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

def _check_email(v):
    if not _EMAIL_RE.match(v):
        raise ValueError(f"Email is the wrong format: {v}")
 
 
def _check_phone(v):
    if not _PHONE_RE.match(v):
        raise ValueError(f"Phone is the wrong format: {v}")
    
# add or delete fields in the FIELDS list, and the rest of the code will automatically handle them.  rmb follow the format below  
FIELDS = [
    {"name": "name",  "type": "TEXT NOT NULL", "validate": None},
    {"name": "email", "type": "TEXT NOT NULL", "validate": _check_email},
    {"name": "phone", "type": "TEXT NOT NULL", "validate": _check_phone},
    # {"name": "address", "type": "TEXT", "validate": None},   # ← optional field example
]
 
FIELD_NAMES = [f["name"] for f in FIELDS]

def validate_user_input(data):
    for field in FIELDS:
        key = field["name"]
        value = data.get(key, "")
        if not value or not value.strip():
            raise ValueError(f"{key.capitalize()} can't be empty")
        if field["validate"]:  # if there is a value
            field["validate"](value.strip()) 

def init_db():
    with get_conn() as conn:
        cols = ", ".join(f"{f['name']} {f['type']}" for f in FIELDS)
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, {cols})"
        )
        conn.commit()

#create user object 

#CREATE
"""
輸入:{"name": "Ken", "email": "ken@gmail.com", "phone": "12345678"}
輸出:{"id": 1, "name": "Ken", "email": "ken@gmail.com", "phone": "12345678"}
"""
def create_user(data):
    validate_user_input(data)
    with get_conn() as conn:
        # ── 砌 cols:"name, email, phone" ──
        cols_parts = []                      # 開一個空 list
        for name in FIELD_NAMES:             # 逐個欄位名
            cols_parts.append(name)          # 加入 list
        cols = ", ".join(cols_parts)         # 用逗號連埋 → "name, email, phone"

        # ── 砌 placeholders:"?, ?, ?" ──
        ph_parts = []                        # 開一個空 list
        for name in FIELD_NAMES:             # 有幾多欄位
            ph_parts.append("?")             # 就加幾多個 "?"
        placeholders = ", ".join(ph_parts)   # 連埋 → "?, ?, ?"

        # ── 砌 values:["Ken", "ken@...", "123"] ──
        values = []                          # 開一個空 list
        for name in FIELD_NAMES:             # 逐個欄位名
            values.append(data[name].strip())  # 去 data 攞值,剪空格,加入 list

        cur = conn.execute(
            f"INSERT INTO users ({cols}) VALUES ({placeholders})",
            values,
        )
        conn.commit()
        return get_user(cur.lastrowid)# return the newly created row as a dict, using the last inserted row id
 
 
#READ 
#輸入:冇
#輸出:[{"id": 1, ...}, {"id": 2, ...}] —— list of dicts
def list_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        result = []                  # empty list
        for r in rows:               # loop rows
            result.append(dict(r))   # change each row to dict and append to list
        return result                # return  list 
 
#搵到:輸入 1 → 輸出 {"id": 1, "name": "Ken", ...}(一個 dict)
def get_user(uid):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
        if row:               # condition to check if row is not None
            return dict(row)  # when there is a row, return it as a dict
        else:
            return None       # when it is empty, return None

 
 
#UPDATE
#成功:輸入 1, {"name": "Kenny", ...} → 輸出 {"id": 1, "name": "Kenny", ...}(更新後)
#ID 唔存在:輸入 99, {...} → 輸出 None
def update_user(uid, data):
    validate_user_input(data) #validate the input before updating the user
    with get_conn() as conn:
        assignments = ", ".join(f"{k} = ?" for k in FIELD_NAMES)  # "name = ?, email = ?, ..."
        values = [data[k].strip() for k in FIELD_NAMES] + [uid]   # 值 + 最後 uid
        cur = conn.execute(
            f"UPDATE users SET {assignments} WHERE id = ?",
            values,
        )
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