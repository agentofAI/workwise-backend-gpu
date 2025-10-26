"""Faiss vector store service (replaces Qdrant)"""
from typing import List, Dict, Any, Optional
from app.config import settings
from app.utils.logger import setup_logger

import os
import json
import faiss
import numpy as np

logger = setup_logger(__name__)

def _normalize(vectors: np.ndarray) -> np.ndarray:
    """L2-normalize vectors so inner product equals cosine similarity."""
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
    return vectors / norms

class VectorStoreService:
    """
    Manages a Faiss index + sidecar payload store.
    - Index: Faiss IndexFlatIP (cosine via normalization)
    - Payloads: JSON list aligned to vector IDs
    - Persistence: saves/loads index + payloads from disk
    """

    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.dimension: Optional[int] = None
        self.payloads: List[Dict[str, Any]] = []
        self.index_path = settings.FAISS_INDEX_PATH
        self.payloads_path = settings.FAISS_PAYLOADS_PATH

        self._load_if_exists()

    # ---------- Persistence ----------

    def _load_if_exists(self):
        """Load index + payloads if the files exist."""
        if os.path.exists(self.index_path) and os.path.exists(self.payloads_path):
            try:
                self.index = faiss.read_index(self.index_path)
                self.dimension = self.index.d  # type: ignore[attr-defined]
                with open(self.payloads_path, "r", encoding="utf-8") as f:
                    self.payloads = json.load(f)
                logger.info(
                    f"Loaded Faiss index ({self.dimension}d) with {self.index.ntotal} vectors"  # type: ignore
                )
            except Exception as e:
                logger.error(f"Failed to load Faiss store; starting fresh. Error: {e}")
                self.index = None
                self.payloads = []
                self.dimension = None

    def _save(self):
        """Persist index + payloads to disk."""
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
        with open(self.payloads_path, "w", encoding="utf-8") as f:
            json.dump(self.payloads, f, ensure_ascii=False)

    # ---------- Collection lifecycle ----------

    def create_collection(self, vector_size: int):
        """
        (Re)create a fresh Faiss index (cosine via normalized vectors).
        WARNING: This clears existing data.
        """
        self.dimension = vector_size
        self.index = faiss.IndexFlatIP(vector_size)  # inner product
        self.payloads = []
        self._save()
        logger.info(f"Created Faiss collection: dim={vector_size}")

    # ---------- Upsert/Search ----------

    def upsert_vectors(
        self,
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]]
    ) -> int:
        """Insert vectors with metadata (IDs are implicit by order)."""
        if self.index is None:
            raise RuntimeError("Faiss index is not initialized. Call create_collection first.")

        arr = np.array(vectors, dtype="float32")
        arr = _normalize(arr)
        self.index.add(arr)  # type: ignore
        self.payloads.extend(payloads)

        self._save()
        logger.info(f"Upserted {len(vectors)} vectors into Faiss")
        return len(vectors)

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Search similar vectors via inner product (cosine)."""
        if self.index is None or self.index.ntotal == 0:  # type: ignore
            return []

        q = np.array([query_vector], dtype="float32")
        q = _normalize(q)
        scores, indices = self.index.search(q, limit)  # type: ignore
        scores = scores[0].tolist()
        indices = indices[0].tolist()

        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores, indices):
            if idx == -1:
                continue
            if score < score_threshold:
                continue
            payload = self.payloads[idx] if 0 <= idx < len(self.payloads) else {}
            results.append({
                "id": idx,
                "score": float(score),
                "payload": payload
            })
        return results

    # ---------- Introspection/Access ----------

    def get_collection_info(self) -> Dict[str, Any]:
        count = int(self.index.ntotal) if self.index is not None else 0  # type: ignore
        return {
            "vectors_count": count,
            "status": "ready" if count >= 0 else "uninitialized"
        }

    def get_all_payloads(self) -> List[Dict[str, Any]]:
        """Return all payloads (used by metrics)."""
        return list(self.payloads)

    def get_payloads_sample(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self.payloads[:limit]

# Global instance
vector_store = VectorStoreService()
