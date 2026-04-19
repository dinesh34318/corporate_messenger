"""
export_rag_data.py — exports all messages to CSV
python backend/export_rag_data.py
"""
import sys, os, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv()

from backend.database import get_all_messages_for_rag

if __name__ == "__main__":
    messages = get_all_messages_for_rag(limit=10000)
    out_path = "chat_export.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["_id","sender","sender_name","conversation_id","content","timestamp"])
        writer.writeheader()
        for m in messages:
            writer.writerow({
                "_id": m.get("_id",""),
                "sender": m.get("sender",""),
                "sender_name": m.get("sender_name",""),
                "conversation_id": m.get("conversation_id",""),
                "content": m.get("content",""),
                "timestamp": m.get("timestamp",""),
            })
    print(f"Exported {len(messages)} messages to {out_path}")
