import re
import bcrypt
from backend.database import (
    get_user_by_login, create_user, update_user_password
)

DEPARTMENTS = {
    "dev": "Development",
    "hrs": "HR",
    "fin": "Finance",
    "mkt": "Marketing",
    "sal": "Sales",
    "sup": "Support",
}

ROLES = {
    "usr": "User",
    "adm": "Admin",
    "mgr": "Manager",
}


def hash_password(plain: str) -> bytes:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt())


def verify_password(plain: str, hashed) -> bool:
    if isinstance(hashed, str):
        hashed = hashed.encode()
    return bcrypt.checkpw(plain.encode(), hashed)


def validate_password_strength(password: str):
    """Returns (ok: bool, message: str)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, "OK"


def generate_login_id(department: str, role: str, sequence: int) -> str:
    dept = department[:3].lower()
    role_code = "adm" if role == "Admin" else ("mgr" if role == "Manager" else "usr")
    seq_str = str(sequence).zfill(6)
    return f"{dept}{role_code}{seq_str}"


def register_user(name: str, department: str, role: str, created_by: str):
    """
    Registers a new user. Returns (login_id, plain_password, error_message).
    Admin generates the credentials and shares them with the user.
    """
    from backend.database import get_db
    db = get_db()
    dept_key = department[:3].lower()
    role_code = "adm" if role == "Admin" else ("mgr" if role == "Manager" else "usr")
    count = db.users.count_documents({"department": department, "role": role})
    sequence = count + 1
    login_id = f"{dept_key}{role_code}{str(sequence).zfill(6)}"

    # default password = login_id (must be changed on first login)
    plain_password = login_id
    hashed = hash_password(plain_password)

    try:
        create_user(
            login_id=login_id,
            hashed_password=hashed,
            name=name,
            department=department,
            role=role,
            created_by=created_by,
        )
        return login_id, plain_password, None
    except Exception as e:
        return None, None, str(e)


def login_user(login_id: str, password: str):
    """Returns (user_doc, error_message)"""
    user = get_user_by_login(login_id)
    if not user:
        return None, "Invalid login ID or password."
    if not user.get("is_active", True):
        return None, "Account is deactivated. Contact your administrator."
    stored = user["password"]
    if isinstance(stored, str):
        stored = stored.encode()
    if not bcrypt.checkpw(password.encode(), stored):
        return None, "Invalid login ID or password."
    return user, None


def change_password(login_id: str, current_password: str, new_password: str):
    """Returns (success: bool, message: str)"""
    user = get_user_by_login(login_id)
    if not user:
        return False, "User not found."
    stored = user["password"]
    if isinstance(stored, str):
        stored = stored.encode()
    if not bcrypt.checkpw(current_password.encode(), stored):
        return False, "Current password is incorrect."
    ok, msg = validate_password_strength(new_password)
    if not ok:
        return False, msg
    if current_password == new_password:
        return False, "New password must be different from the current password."
    hashed = hash_password(new_password)
    update_user_password(login_id, hashed)
    return True, "Password changed successfully."
