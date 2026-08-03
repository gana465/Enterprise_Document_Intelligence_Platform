"""
auth.py
----------------------------------------
Authentication Module
Enterprise Document Intelligence Platform
----------------------------------------
"""

from datetime import datetime

import bcrypt
from sqlalchemy import or_

from database import session_scope
from models import User


# ----------------------------------------------------
# Password Hashing
# ----------------------------------------------------

def hash_password(password: str) -> str:
    """
    Convert plain password into bcrypt hash.
    """

    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    )

    return hashed.decode("utf-8")


# ----------------------------------------------------
# Verify Password
# ----------------------------------------------------

def verify_password(
    plain_password: str,
    password_hash: str
) -> bool:
    """
    Compare user password with stored hash.
    """

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        password_hash.encode("utf-8")
    )


# ----------------------------------------------------
# Validate Password Strength
# ----------------------------------------------------

def validate_password(password: str):

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if not any(c.isupper() for c in password):
        return False, "Password must contain an uppercase letter."

    if not any(c.islower() for c in password):
        return False, "Password must contain a lowercase letter."

    if not any(c.isdigit() for c in password):
        return False, "Password must contain a number."

    return True, ""


# ----------------------------------------------------
# Username Exists
# ----------------------------------------------------

def username_exists(username: str):

    with session_scope() as db:

        return (
            db.query(User)
            .filter(User.username == username)
            .first()
            is not None
        )


# ----------------------------------------------------
# Email Exists
# ----------------------------------------------------

def email_exists(email: str):

    with session_scope() as db:

        return (
            db.query(User)
            .filter(User.email == email)
            .first()
            is not None
        )


# ----------------------------------------------------
# Register User
# ----------------------------------------------------

def register_user(
    username: str,
    email: str,
    password: str
):

    username = username.strip()

    email = email.strip().lower()

    ok, message = validate_password(password)

    if not ok:
        return False, message

    with session_scope() as db:

        existing = (
            db.query(User)
            .filter(
                or_(
                    User.username == username,
                    User.email == email
                )
            )
            .first()
        )

        if existing:

            return (
                False,
                "Username or email already exists."
            )

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )

        db.add(user)

    return (
        True,
        "Registration successful."
    )


# ----------------------------------------------------
# Login User
# ----------------------------------------------------

def authenticate_user(
    username: str,
    password: str
):

    with session_scope() as db:

        user = (
            db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if user is None:

            return None

        if not user.is_active:

            return None

        if not verify_password(
            password,
            user.password_hash
        ):

            return None

        user.last_login = datetime.utcnow()

        return user


# ----------------------------------------------------
# Get User By ID
# ----------------------------------------------------

def get_user(user_id: int):

    with session_scope() as db:

        return (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )


# ----------------------------------------------------
# Change Password
# ----------------------------------------------------

def change_password(
    user_id: int,
    old_password: str,
    new_password: str
):

    ok, msg = validate_password(new_password)

    if not ok:
        return False, msg

    with session_scope() as db:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user is None:

            return False, "User not found."

        if not verify_password(
            old_password,
            user.password_hash
        ):

            return False, "Old password is incorrect."

        user.password_hash = hash_password(new_password)

    return True, "Password updated successfully."


# ----------------------------------------------------
# Deactivate User
# ----------------------------------------------------

def deactivate_user(user_id: int):

    with session_scope() as db:

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if user:

            user.is_active = False

            return True

    return False