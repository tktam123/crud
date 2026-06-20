import os
import re

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, validates

# ── Configuration ───────────────────────────────────────────────
DB_PATH = os.environ.get("DB_PATH", "leangains.db")

engine = create_engine(f"sqlite:///{DB_PATH}",echo=True) 
# expire_on_commit=False: after commit(), keep attribute values on the
# object instead of marking them "stale" and forcing a re-query on next
# access. Without this, reading user.name after delete_user() commits
# would try to re-fetch a row that no longer exists and raise an error.
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()


# ── Validation patterns (same rules as before, just relocated) ──
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^[0-9+\-\s()]{7,20}$")
_ADDRESS_RE = re.compile(r"^(?=.*[A-Za-z0-9]).{3,100}$")


class User(Base):
    """ORM model for the users table.

    This class IS the schema: each Column below replaces one entry
    that used to live in crud.py's FIELDS list, AND it replaces the
    manual CREATE TABLE string that init_db() used to build.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)

    # ── Validators ────────────────────────────────────────────
    # This runs automatically the moment you do `user.email = "..."`
    # or `User(email="...")` — no separate validate_user_input() call
    # needed before saving. Raising ValueError stops the assignment.
    # (SQLAlchemy only allows one @validates per attribute, so all four
    # fields are checked through this single dispatcher.)

    _FORMAT_CHECKS = {
        "email": (_EMAIL_RE, "Email is the wrong format: {value}"),
        "phone": (_PHONE_RE, "Phone is the wrong format: {value}"),
        "address": (_ADDRESS_RE, "Address is the wrong format: {value}"),
    }

    @validates("name", "email", "phone", "address")
    def _validate_field(self, key, value):
        if value is None or not value.strip():
            raise ValueError(f"{key.capitalize()} can't be empty")
        value = value.strip()

        check = self._FORMAT_CHECKS.get(key)
        if check:
            pattern, message = check
            if not pattern.match(value):
                raise ValueError(message.format(value=value))
        return value

    def __repr__(self):
        return f"<User id={self.id} name={self.name!r}>"


# Field names in display order — manage.py uses this for the table
# header/columns, same role FIELD_NAMES played before.
FIELD_NAMES = ["name", "email", "phone", "address"]


def init_db():
    """Create the users table if it doesn't exist yet."""
    Base.metadata.create_all(engine)
