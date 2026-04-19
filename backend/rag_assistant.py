import os
import groq
from backend.rag_indexer import query_index

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


def ask_assistant(question: str, user_login: str, user_name: str = "") -> str:
    """
    Retrieves relevant chat context via RAG and asks Claude to answer.
    Returns the assistant's response string.
    """
    try:
        results = query_index(question, n_results=12)
    except Exception as e:
        results = []

    if not results:
        context_block = "No relevant chat history found in the database."
    else:
        lines = []
        for doc, meta in results:
            sender = meta.get("sender_name") or meta.get("sender", "Unknown")
            ts = meta.get("timestamp", "")
            lines.append(f"[{ts[:16]}] {sender}: {doc}")
        context_block = "\n".join(lines)

    system_prompt = (
        "You are a smart corporate assistant for an internal messaging platform. "
        "Your job is to help employees understand their schedules, tasks, project statuses, "
        "and team discussions based on the company chat history provided to you. "
        "Always be concise, professional, and helpful. "
        "If you cannot find the answer in the context, say so clearly. "
        "Never invent information that is not present in the chat history."
    )

    user_prompt = (
        f"The user asking is: {user_name or user_login} (login: {user_login})\n\n"
        f"Relevant chat history context:\n"
        f"---\n{context_block}\n---\n\n"
        f"User question: {question}\n\n"
        "Please answer based on the chat history above."
    )

    try:
        client = _get_client()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=1000,
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI assistant error: {str(e)}"


def summarise_tasks_for_user(user_login: str, tasks: list) -> str:
    """Use Claude to generate a natural language summary of the user's pending tasks."""
    if not tasks:
        return "You have no pending tasks at the moment."

    task_lines = []
    for t in tasks[:15]:
        due = t.get("due_date")
        due_str = due.strftime("%b %d, %Y %H:%M") if due else "No deadline"
        task_lines.append(f"- [{t.get('task_type','task').upper()}] {t['title']} | Due: {due_str} | Status: {t.get('status','pending')}")

    tasks_block = "\n".join(task_lines)

    try:
        client = _get_client()
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=400,
            messages=[{
                "role": "user",
                "content": (
                    f"Here are the pending tasks for employee {user_login}:\n{tasks_block}\n\n"
                    "Write a brief, friendly 3-4 sentence summary of their workload and priorities. "
                    "Be professional and motivating."
                )
            }]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Could not generate summary: {str(e)}"
