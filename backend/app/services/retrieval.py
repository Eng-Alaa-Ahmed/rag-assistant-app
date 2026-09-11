import logging

import chromadb
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = logging.getLogger(__name__)

_embedder = None
_collection = None


def load_vector_store():
    global _embedder, _collection

    logger.info("Loading embedding model: %s", settings.embedding_model_name)
    _embedder = SentenceTransformer(settings.embedding_model_name)

    logger.info("Loading persisted vector store from: %s", settings.vector_store_path)
    client = chromadb.PersistentClient(path=settings.vector_store_path)
    _collection = client.get_collection(settings.collection_name)
    logger.info("Vector store loaded: %d chunks available", _collection.count())


def is_ready():
    return _embedder is not None and _collection is not None


def retrieve(query: str, top_k=None):
    if not is_ready():
        raise RuntimeError("Vector store is not loaded yet.")

    top_k = top_k or settings.top_k
    query_embedding = _embedder.encode([query])[0].tolist()

    results = _collection.query(query_embeddings=[query_embedding], n_results=top_k)

    retrieved = []
    for i in range(len(results["documents"][0])):
        retrieved.append({
            "text": results["documents"][0][i],
            "page_number": results["metadatas"][0][i].get("page_number"),
            "distance": results["distances"][0][i],
        })
    return retrieved
