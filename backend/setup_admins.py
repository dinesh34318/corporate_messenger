"""
setup_admins.py
Run once to create default admin accounts: python backend/setup_admins.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()

from backend.auth import hash_password
from backend.database import get_db

ADMINS = [
    {"login_id": "devadm000000", "name": "Dev Admin",     "department": "Development", "role": "Admin"},
    {"login_id": "hrsadm000000", "name": "HR Admin",      "department": "HR",          "role": "Admin"},
    {"login_id": "finadm000000", "name": "Finance Admin",  "department": "Finance",     "role": "Admin"},
    {"login_id": "mktadm000000", "name": "Marketing Admin","department": "Marketing",   "role": "Admin"},
    {"login_id": "saladm000000", "name": "Sales Admin",    "department": "Sales",       "role": "Admin"},
    {"login_id": "supadm000000", "name": "Support Admin",  "department": "Support",     "role": "Admin"},
]

def seed_admins():
    db = get_db()
    created, skipped = 0, 0
    for a in ADMINS:
        existing = db.users.find_one({"login_id": a["login_id"]})
        if existing:
            print(f"  [SKIP] {a['login_id']} already exists.")
            skipped += 1
            continue
        hashed = hash_password(a["login_id"])  # default password = login_id
        db.users.insert_one({
            "login_id": a["login_id"],
            "password": hashed,
            "name": a["name"],
            "department": a["department"],
            "role": a["role"],
            "password_changed": False,
            "is_active": True,
            "created_by": "system",
        })
        print(f"  [OK]   {a['login_id']} created (password: {a['login_id']})")
        created += 1
    print(f"\nDone. {created} created, {skipped} skipped.")

if __name__ == "__main__":
    seed_admins()
