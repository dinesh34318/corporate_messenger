"""
rag_watcher.py
Run this in the background: python backend/rag_watcher.py
It watches for new unindexed messages, indexes them into ChromaDB,
and auto-creates tasks from actionable/meeting messages.
"""
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from backend.database import get_unindexed_messages, mark_messages_indexed, get_conversation, create_task
from backend.rag_indexer import index_messages
from backend.rag_extractor import extract_task_from_message


def process_new_messages():
    messages = get_unindexed_messages()
    if not messages:
        return 0

    # Index into ChromaDB
    indexed_count = index_messages(messages)
    ids = [m["_id"] for m in messages]

    # Extract tasks from each message
    tasks_created = 0
    for msg in messages:
        conv_id = str(msg.get("conversation_id", ""))
        if not conv_id:
            continue
        conv = get_conversation(conv_id)
        if not conv:
            continue
        participants = conv.get("participants", [])
        extracted = extract_task_from_message(
            text=msg.get("content", ""),
            sender=msg.get("sender", ""),
            sender_name=msg.get("sender_name", ""),
            conversation_id=conv_id,
            message_id=str(msg["_id"]),
            participants=participants,
        )
        for task in extracted:
            create_task(**task)
            tasks_created += 1

    mark_messages_indexed(ids)
    print(f"[Watcher] Indexed {indexed_count} messages, created {tasks_created} tasks.")
    return indexed_count


if __name__ == "__main__":
    print("[Watcher] Starting RAG watcher... (Ctrl+C to stop)")
    while True:
        try:
            process_new_messages()
        except Exception as e:
            print(f"[Watcher] Error: {e}")
        time.sleep(5)
