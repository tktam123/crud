from sqlalchemy.exc import SQLAlchemyError

from models import User, SessionLocal, FIELD_NAMES, init_db  # noqa: F401  (FIELD_NAMES re-exported for manage.py)


class DatabaseError(Exception):  # same role as before: wraps DB-level failures
    pass


def get_session():
    try:
        return SessionLocal()
    except SQLAlchemyError as error:
        raise DatabaseError(
            "Cannot open the database file. Check the DB_PATH and folder permissions."
        ) from error


# CREATE
# input: {"name": "Ken", "email": "ken@gmail.com", "phone": "12345678", "address": "1 Elvet Hill"}
# output: User object (validated by the model's @validates methods)
def create_user(data):
    with get_session() as session:
        user = User(
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            address=data.get("address", ""),
        )
        session.add(user)
        session.commit()
        session.refresh(user)  # pulls back the autoincrement id
        return user


# READ
# input: nothing
# output: list of User objects, ordered by id
def list_users():
    with get_session() as session:
        return session.query(User).order_by(User.id).all()


# input: uid = 1
# output: a single User object, or None if it doesn't exist
def get_user(uid):
    with get_session() as session:
        return session.get(User, uid)


# UPDATE
# input: uid = 1, {"name": "Kenny", "email": "...", "phone": "...", "address": "..."}
# output: the updated User object, or None if uid doesn't exist
def update_user(uid, data):
    with get_session() as session:
        user = session.get(User, uid)
        if user is None:
            return None
        # Assigning each attribute triggers the model's @validates methods,
        # same as the old validate_user_input() call used to.
        user.name = data.get("name", "")
        user.email = data.get("email", "")
        user.phone = data.get("phone", "")
        user.address = data.get("address", "")
        session.commit()
        session.refresh(user)
        return user


# DELETE
# input: uid = 1
# output: the deleted User object (detached from the session), or None
def delete_user(uid):
    with get_session() as session:
        user = session.get(User, uid)
        if user is None:
            return None
        session.delete(user)
        session.commit()
        return user