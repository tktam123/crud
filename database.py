import psycopg
from psycopg.rows import dict_row


CONN_STR = "postgresql://postgres:(password)@localhost:5432/leangains"

def get_conn():
    # 同 SQLite 唔同:呢度接通嘅係一個行緊嘅 server,唔係一個檔案
    # row_factory=dict_row 等於 SQLite 嗰句 conn.row_factory = sqlite3.Row
    return psycopg.connect(CONN_STR, row_factory=dict_row)

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,          -- SQLite 係 INTEGER ... AUTOINCREMENT
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        conn.commit()

# CREATE
def create_user(name, email):
    with get_conn() as conn:
        # placeholder 由 ? 變做 %s;攞返新 id 用 RETURNING,唔係 lastrowid
        row = conn.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING *",
            (name, email)
        ).fetchone()
        conn.commit()
        return row                       # dict_row 已經直接俾返 dict

# READ
def list_users():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        return rows                      # 已經係 list of dict,唔使再 dict(r)

def get_user(uid):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = %s", (uid,)).fetchone()
        return row                       # 搵唔到會係 None

# UPDATE
def update_user(uid, name, email):
    with get_conn() as conn:
        row = conn.execute(
            "UPDATE users SET name = %s, email = %s WHERE id = %s RETURNING *",
            (name, email, uid)
        ).fetchone()
        conn.commit()
        return row

# DELETE
def delete_user(uid):
    with get_conn() as conn:
        row = conn.execute(
            "DELETE FROM users WHERE id = %s RETURNING *", (uid,)
        ).fetchone()
        conn.commit()
        return row