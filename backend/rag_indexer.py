import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from backend.database import get_all_messages_for_rag, get_unindexed_messages, mark_messages_indexed

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_store")
COLLECTION_NAME = "chat_messages"

_model = None
_client = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def index_messages(messages: list):
    if not messages:
        return 0
    col = _get_collection()
    model = _get_model()

    texts, ids, metadatas = [], [], []
    for msg in messages:
        text = msg.get("content", "").strip()
        if not text:
            continue
        mid = str(msg["_id"])
        texts.append(text)
        ids.append(mid)
        metadatas.append({
            "sender": msg.get("sender", ""),
            "sender_name": msg.get("sender_name", ""),
            "conversation_id": str(msg.get("conversation_id", "")),
            "timestamp": str(msg.get("timestamp", "")),
        })

    if not texts:
        return 0

    embeddings = model.encode(texts).tolist()
    col.upsert(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)
    return len(texts)


def seed_index():
    """Index ALL existing messages."""
    messages = get_all_messages_for_rag()
    count = index_messages(messages)
    ids = [str(m["_id"]) for m in messages]
    mark_messages_indexed(ids)
    print(f"[RAG] Seeded {count} messages into ChromaDB.")
    return count


def index_new_messages():
    """Index only unindexed messages."""
    messages = get_unindexed_messages()
    if not messages:
        return 0
    count = index_messages(messages)
    ids = [str(m["_id"]) for m in messages]
    mark_messages_indexed(ids)
    return count


def query_index(query_text: str, n_results: int = 10):
    """Returns top N relevant messages for a query."""
    col = _get_collection()
    model = _get_model()
    embedding = model.encode([query_text]).tolist()
    results = col.query(query_embeddings=embedding, n_results=n_results)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    return list(zip(docs, metas))
