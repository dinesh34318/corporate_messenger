import re
from datetime import datetime, timedelta
from dateutil import parser as dateparser


MEETING_KEYWORDS = [
    "meeting", "call", "standup", "sync", "review", "demo", "presentation",
    "interview", "discussion", "session", "workshop", "webinar", "briefing",
    "conference", "huddle", "check-in", "1:1", "one-on-one"
]

TASK_KEYWORDS = [
    "please", "could you", "can you", "need you to", "required",
    "submit", "complete", "finish", "send", "prepare", "review",
    "update", "fix", "deploy", "push", "deliver", "upload",
    "deadline", "due", "by eod", "by end of day", "asap", "urgent",
    "implement", "build", "create", "develop", "test", "check"
]

TIME_PATTERNS = [
    r'\b(\d{1,2})\s*(?::|\.)\s*(\d{2})\s*(am|pm)?\b',
    r'\b(\d{1,2})\s*(am|pm)\b',
    r'\b(tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    r'\b(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\b',
    r'\bnext\s+(week|monday|tuesday|wednesday|thursday|friday)\b',
]

DATE_WORDS = {
    "today": 0, "tomorrow": 1, "monday": None, "tuesday": None,
    "wednesday": None, "thursday": None, "friday": None,
    "saturday": None, "sunday": None,
}


def is_meeting_message(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in MEETING_KEYWORDS)


def is_task_message(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in TASK_KEYWORDS)


def extract_time_mentions(text: str):
    lower = text.lower()
    found = []
    for pattern in TIME_PATTERNS:
        matches = re.findall(pattern, lower, re.IGNORECASE)
        if matches:
            found.extend(matches)
    return found


def guess_due_date(text: str):
    lower = text.lower()
    now = datetime.utcnow()

    if "today" in lower or "eod" in lower or "end of day" in lower:
        return now.replace(hour=18, minute=0, second=0)
    if "tomorrow" in lower:
        return (now + timedelta(days=1)).replace(hour=9, minute=0, second=0)
    if "asap" in lower or "urgent" in lower:
        return now + timedelta(hours=4)

    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(days):
        if day in lower:
            current_weekday = now.weekday()
            days_ahead = i - current_weekday
            if days_ahead <= 0:
                days_ahead += 7
            return (now + timedelta(days=days_ahead)).replace(hour=9, minute=0, second=0)

    # Try dateutil parsing on substrings
    words = text.split()
    for i in range(len(words) - 1):
        chunk = " ".join(words[i:i+3])
        try:
            dt = dateparser.parse(chunk, fuzzy=True)
            if dt and dt > now:
                return dt
        except Exception:
            pass

    return None


def extract_task_from_message(text: str, sender: str, sender_name: str, conversation_id: str, message_id: str, participants: list):
    """
    Analyses a message and returns a list of task dicts to create.
    Returns [] if no actionable task is detected.
    """
    tasks = []

    if not (is_meeting_message(text) or is_task_message(text)):
        return tasks

    lower = text.lower()
    due_date = guess_due_date(text)

    # Meeting detection
    if is_meeting_message(text):
        meeting_type = next((kw for kw in MEETING_KEYWORDS if kw in lower), "meeting")
        title = f"📅 {meeting_type.title()} scheduled"
        description = f"Auto-detected from message by {sender_name or sender}:\n\n\"{text}\""
        for participant in participants:
            if participant != sender:
                tasks.append({
                    "title": title,
                    "description": description,
                    "assigned_to": participant,
                    "assigned_by": sender,
                    "due_date": due_date,
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "task_type": "meeting",
                })

    # Action/task detection (only for direct action words)
    elif is_task_message(text):
        action_kw = next((kw for kw in TASK_KEYWORDS if kw in lower), "task")
        title = f"📋 Action required: {action_kw.title()}"
        description = f"Auto-detected task from {sender_name or sender}:\n\n\"{text}\""
        for participant in participants:
            if participant != sender:
                tasks.append({
                    "title": title,
                    "description": description,
                    "assigned_to": participant,
                    "assigned_by": sender,
                    "due_date": due_date,
                    "conversation_id": conversation_id,
                    "message_id": message_id,
                    "task_type": "action",
                })

    return tasks
