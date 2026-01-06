import hashlib
from dotenv import load_dotenv
load_dotenv()

import os, httpx
from typing import List, Tuple, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import uuid

QDRANT_URL = os.getenv("QDRANT_URL","http://qdrant:6333")
COLLECTION = os.getenv("COLLECTION","tnf_chunks")
EMBED_MODEL = os.getenv("EMBED_MODEL","nomic-embed-text")
LLM_BASE = os.getenv("LLM_BASE","http://ollama:11434")

_client = QdrantClient(url=QDRANT_URL)

def ensure_collection():
    names = [c.name for c in _client.get_collections().collections]
    if COLLECTION not in names:
        _client.recreate_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )

def embed(texts: List[str]) -> List[List[float]]:
    with httpx.Client(timeout=120) as cx:
        out = []
        for t in texts:
            r = cx.post(f"{LLM_BASE}/api/embeddings", json={"model": EMBED_MODEL, "prompt": t})
            r.raise_for_status()
            out.append(r.json()["embedding"])
        return out

def upsert_chunks(chunks):
    ensure_collection()
    vecs = embed([c[0] for c in chunks])
    points = []
    for ((text, meta), vec) in zip(chunks, vecs):
        stable = f"{meta.get('file','?')}|{meta.get('page','?')}|{text}"
        pid = str(uuid.uuid5(uuid.NAMESPACE_URL, stable))  # deterministic & valid
        points.append(PointStruct(id=pid, vector=vec, payload={"text": text, **meta}))
    _client.upsert(collection_name=COLLECTION, points=points)
    
def search_chunks(query: str, k: int=6) -> List[Tuple[str, Dict[str, Any]]]:
    ensure_collection()
    qv = embed([query])[0]
    res = _client.search(collection_name=COLLECTION, query_vector=qv, limit=k)
    out = []
    for p in res:
        payload = p.payload
        out.append((payload["text"], {k:v for k,v in payload.items() if k!="text"}))
    return out
