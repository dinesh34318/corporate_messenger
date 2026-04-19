import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "")
DB_NAME = os.getenv("DB_NAME", "chatapp1")

_client = None
_db = None


def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGODB_URI)
        _db = _client[DB_NAME]
        _ensure_indexes()
    return _db


def _ensure_indexes():
    db = _db
    db.users.create_index([("login_id", ASCENDING)], unique=True)
    db.conversations.create_index([("participants", ASCENDING)])
    db.messages.create_index([("conversation_id", ASCENDING), ("timestamp", ASCENDING)])
    db.tasks.create_index([("assigned_to", ASCENDING)])
    db.tasks.create_index([("conversation_id", ASCENDING)])


# ─── USER HELPERS ────────────────────────────────────────────────────────────

def get_user_by_login(login_id: str):
    return get_db().users.find_one({"login_id": login_id})


def get_user_by_id(user_id):
    return get_db().users.find_one({"_id": ObjectId(str(user_id))})


def get_all_users(exclude_login=None):
    query = {}
    if exclude_login:
        query["login_id"] = {"$ne": exclude_login}
    return list(get_db().users.find(query, {"password": 0}))


def get_users_by_department(department: str):
    return list(get_db().users.find({"department": department}, {"password": 0}))


def create_user(login_id, hashed_password, name, department, role, created_by=None):
    user = {
        "login_id": login_id,
        "password": hashed_password,
        "name": name,
        "department": department,
        "role": role,
        "password_changed": False,
        "created_at": datetime.utcnow(),
        "created_by": created_by,
        "is_active": True,
    }
    result = get_db().users.insert_one(user)
    return result.inserted_id


def update_user_password(login_id: str, new_hashed: bytes):
    get_db().users.update_one(
        {"login_id": login_id},
        {"$set": {"password": new_hashed, "password_changed": True}}
    )


def deactivate_user(login_id: str):
    get_db().users.update_one({"login_id": login_id}, {"$set": {"is_active": False}})


# ─── CONVERSATION HELPERS ─────────────────────────────────────────────────────

def get_or_create_direct_conversation(login_a: str, login_b: str):
    db = get_db()
    participants = sorted([login_a, login_b])
    conv = db.conversations.find_one({
        "type": "direct",
        "participants": {"$all": participants, "$size": 2}
    })
    if conv:
        return str(conv["_id"])
    result = db.conversations.insert_one({
        "type": "direct",
        "participants": participants,
        "created_at": datetime.utcnow(),
    })
    return str(result.inserted_id)


def create_group_conversation(name: str, participants: list, created_by: str):
    db = get_db()
    result = db.conversations.insert_one({
        "type": "group",
        "name": name,
        "participants": participants,
        "created_by": created_by,
        "created_at": datetime.utcnow(),
    })
    return str(result.inserted_id)


def get_user_conversations(login_id: str):
    db = get_db()
    convs = list(db.conversations.find({"participants": login_id}))
    enriched = []
    for c in convs:
        last_msg = db.messages.find_one(
            {"conversation_id": str(c["_id"])},
            sort=[("timestamp", DESCENDING)]
        )
        c["last_message"] = last_msg
        c["_id"] = str(c["_id"])
        enriched.append(c)
    enriched.sort(
        key=lambda x: x["last_message"]["timestamp"] if x.get("last_message") else x["created_at"],
        reverse=True
    )
    return enriched


def get_conversation(conv_id: str):
    db = get_db()
    return db.conversations.find_one({"_id": ObjectId(conv_id)})


# ─── MESSAGE HELPERS ──────────────────────────────────────────────────────────

def send_message(conversation_id: str, sender_login: str, content: str, sender_name: str = ""):
    db = get_db()
    msg = {
        "conversation_id": conversation_id,
        "sender": sender_login,
        "sender_name": sender_name,
        "content": content,
        "timestamp": datetime.utcnow(),
        "indexed": False,
    }
    result = db.messages.insert_one(msg)
    return str(result.inserted_id)


def get_messages(conversation_id: str, limit: int = 100):
    db = get_db()
    msgs = list(db.messages.find(
        {"conversation_id": conversation_id},
        sort=[("timestamp", ASCENDING)],
        limit=limit
    ))
    for m in msgs:
        m["_id"] = str(m["_id"])
    return msgs


def get_all_messages_for_rag(limit: int = 2000):
    db = get_db()
    msgs = list(db.messages.find({}, sort=[("timestamp", DESCENDING)], limit=limit))
    for m in msgs:
        m["_id"] = str(m["_id"])
    return msgs


def get_unindexed_messages():
    db = get_db()
    msgs = list(db.messages.find({"indexed": False}))
    for m in msgs:
        m["_id"] = str(m["_id"])
    return msgs


def mark_messages_indexed(message_ids: list):
    db = get_db()
    object_ids = [ObjectId(mid) for mid in message_ids]
    db.messages.update_many(
        {"_id": {"$in": object_ids}},
        {"$set": {"indexed": True}}
    )


# ─── TASK HELPERS ─────────────────────────────────────────────────────────────

def create_task(title: str, description: str, assigned_to: str, assigned_by: str,
                due_date=None, conversation_id: str = None, message_id: str = None,
                task_type: str = "general"):
    db = get_db()
    task = {
        "title": title,
        "description": description,
        "assigned_to": assigned_to,
        "assigned_by": assigned_by,
        "due_date": due_date,
        "conversation_id": conversation_id,
        "message_id": message_id,
        "task_type": task_type,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "seen": False,
    }
    result = db.tasks.insert_one(task)
    return str(result.inserted_id)


def get_user_tasks(login_id: str):
    db = get_db()
    tasks = list(db.tasks.find({"assigned_to": login_id}, sort=[("created_at", DESCENDING)]))
    for t in tasks:
        t["_id"] = str(t["_id"])
    return tasks


def get_tasks_assigned_by(login_id: str):
    db = get_db()
    tasks = list(db.tasks.find({"assigned_by": login_id}, sort=[("created_at", DESCENDING)]))
    for t in tasks:
        t["_id"] = str(t["_id"])
    return tasks


def update_task_status(task_id: str, status: str):
    db = get_db()
    db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": status, "updated_at": datetime.utcnow()}})


def mark_task_seen(task_id: str):
    db = get_db()
    db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"seen": True}})


def get_unseen_task_count(login_id: str):
    db = get_db()
    return db.tasks.count_documents({"assigned_to": login_id, "seen": False})


# ─── CALENDAR / EVENTS ───────────────────────────────────────────────────────

def save_event(login_id: str, date_str: str, title: str, note: str = ""):
    db = get_db()
    existing = db.events.find_one({"login_id": login_id, "date": date_str, "title": title})
    if existing:
        db.events.update_one(
            {"_id": existing["_id"]},
            {"$set": {"note": note, "updated_at": datetime.utcnow()}}
        )
        return str(existing["_id"])
    result = db.events.insert_one({
        "login_id": login_id,
        "date": date_str,
        "title": title,
        "note": note,
        "created_at": datetime.utcnow(),
    })
    return str(result.inserted_id)


def get_events_for_date(login_id: str, date_str: str):
    db = get_db()
    return list(db.events.find({"login_id": login_id, "date": date_str}))


def get_all_events_for_user(login_id: str):
    db = get_db()
    return list(db.events.find({"login_id": login_id}))
