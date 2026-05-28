import os
import time
import chromadb
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Initialise the embedding model and ChromaDB
# all-MiniLM-L6-v2 is small, fast, and free — ideal for a portfolio project
# ---------------------------------------------------------------------------

# Load once at startup — this downloads the model on first run (~80MB)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB stores vectors locally in a folder called chroma_db/
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="conversations")


def store_turn(session_id: str, user_msg: str, assistant_msg: str) -> None:
    """
    Embeds and stores a conversation turn (user + assistant) in ChromaDB.
    Called after every successful chat response.
    """
    # Combine both sides of the turn into one chunk for embedding
    text = f"User: {user_msg}\nAssistant: {assistant_msg}"
    embedding = embedding_model.encode(text).tolist()

    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[f"{session_id}_{int(time.time() * 1000)}"],
        metadatas=[{"session_id": session_id, "timestamp": int(time.time())}]
    )


def retrieve_context(query: str, session_id: str, n_results: int = 3) -> str:
    """
    Finds the most semantically similar past turns to the current query.
    Returns them as a formatted string to inject into Claude's system prompt.
    """
    query_embedding = embedding_model.encode(query).tolist()

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"session_id": session_id}  # Only retrieve this user's history
        )
        documents = results.get("documents", [[]])[0]
        if not documents:
            return ""
        return "\n---\n".join(documents)
    except Exception:
        # If not enough data in DB yet, return empty string
        return ""