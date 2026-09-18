import os
import chromadb
from sentence_transformers import SentenceTransformer
from src.config import settings

# Load model globally to avoid reloading per request
try:
    _model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    _model = None
    print(f"Warning: Could not load SentenceTransformer: {e}")

# Initialize Chroma client
try:
    _client = chromadb.PersistentClient(path=settings.chroma_db_dir)
    _collection = _client.get_or_create_collection(name="verdant_corpus")
except Exception as e:
    _client = None
    _collection = None
    print(f"Warning: Could not initialize ChromaDB: {e}")

def query_corpus(query: str, top_k: int = 3, filter_source_ids: list = None):
    """
    Query the corpus for evidence related to the query.
    Optionally filter by a list of source_ids (e.g. the sources linked to a surviving card).
    """
    if _model is None or _collection is None:
        return []

    try:
        if _collection.count() == 0:
            return [] # Gracefully handle empty corpus
    except Exception:
        return []

    query_embedding = _model.encode([query]).tolist()
    
    where_clause = None
    if filter_source_ids and len(filter_source_ids) > 0:
        if len(filter_source_ids) == 1:
            where_clause = {"source_id": filter_source_ids[0]}
        else:
            where_clause = {"source_id": {"$in": filter_source_ids}}

    results = _collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where=where_clause,
        include=["documents", "metadatas", "distances"]
    )
    
    retrieved_chunks = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        dists = results["distances"][0]
        
        for doc, meta, dist in zip(docs, metas, dists):
            retrieved_chunks.append({
                "text": doc,
                "metadata": meta,
                "score": float(dist) # distance score
            })
            
    return retrieved_chunks
