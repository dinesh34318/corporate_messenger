"""
test_connection.py  — run to verify MongoDB connectivity
python backend/test_connection.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()

from backend.database import get_db

if __name__ == "__main__":
    try:
        db = get_db()
        db.command("ping")
        print("[OK] MongoDB connection successful.")
        print(f"     Collections: {db.list_collection_names()}")
    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
