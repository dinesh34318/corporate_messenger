"""
seed_index.py
Run once to index all existing messages: python backend/seed_index.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()

from backend.rag_indexer import seed_index

if __name__ == "__main__":
    count = seed_index()
    print(f"Done. {count} messages indexed.")
