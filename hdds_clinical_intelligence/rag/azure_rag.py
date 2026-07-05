"""
Azure RAG backend -- our own real retrieval-augmented generation.

This is the BACKUP plan: if the EY GDX RAG system is unavailable, this provides a
genuine RAG pipeline (not keyword matching):

    1. Split each patient's clinical notes into chunks.
    2. Embed chunks with Azure OpenAI embeddings; cache the vectors on disk so we
       don't re-embed on every request.
    3. On a query, embed the query and rank chunks by cosine similarity.
    4. Synthesize an answer with the Azure OpenAI chat model, grounded ONLY in the
       retrieved chunks, and return the supporting chunks as citations.

Requires Azure OpenAI env vars (see llm/azure_client.py). The factory only selects
this backend when those are configured.
"""

import os
import json
import math
import hashlib
from typing import List, Dict, Any

from rag.base import BaseRAGSystem
from rag.notes_loader import load_notes_by_patient, BASE_DIR
from llm import azure_client

INDEX_PATH = os.path.join(BASE_DIR, "data", "processed", "rag_vector_index.json")
CHUNK_CHARS = 700  # ~150-200 tokens per chunk; small notes stay whole


def _chunk(text: str) -> List[str]:
    text = text.strip()
    if len(text) <= CHUNK_CHARS:
        return [text] if text else []
    return [text[i:i + CHUNK_CHARS] for i in range(0, len(text), CHUNK_CHARS)]


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


class AzureRAGSystem(BaseRAGSystem):
    name = "azure-rag"

    def __init__(self):
        self.notes_db = load_notes_by_patient()
        self._index = self._load_index()  # {chunk_hash: {"text","patient_id","embedding"}}

    # ---- index persistence ----
    def _load_index(self) -> Dict[str, dict]:
        if os.path.exists(INDEX_PATH):
            try:
                with open(INDEX_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_index(self):
        os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
        with open(INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(self._index, f)

    def _ensure_embedded(self, patient_id: str) -> List[dict]:
        """Return indexed chunks for a patient, embedding+caching any that are new."""
        chunks = []
        for note in self.notes_db.get(patient_id, []):
            for piece in _chunk(note.get("text", "")):
                h = hashlib.sha256(piece.encode("utf-8")).hexdigest()
                chunks.append((h, piece))

        missing = [(h, p) for h, p in chunks if h not in self._index]
        if missing:
            vectors = azure_client.embed([p for _, p in missing])
            for (h, p), vec in zip(missing, vectors):
                self._index[h] = {"text": p, "patient_id": patient_id, "embedding": vec}
            self._save_index()

        return [self._index[h] for h, _ in chunks if h in self._index]

    # ---- BaseRAGSystem ----
    def retrieve(self, patient_id: str, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        indexed = self._ensure_embedded(patient_id)
        if not indexed:
            return []
        q_vec = azure_client.embed([query])[0]
        scored = [
            {
                "text": c["text"],
                "score": _cosine(q_vec, c["embedding"]),
                "source": "asclepius_notes.json",
            }
            for c in indexed
        ]
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def extract_information(self, patient_id: str, query_type: str = "all") -> Any:
        notes = self.notes_db.get(patient_id, [])
        if not notes:
            return "No unstructured clinical notes available."

        query = ("Summarize the most critical clinical findings, risks, and any "
                 "recommended follow-up for this patient.")
        top = self.retrieve(patient_id, query, top_k=4)
        full_text = " ".join(n["text"] for n in notes)

        # Grounded synthesis over ONLY the retrieved chunks.
        context = "\n\n".join(f"[{i+1}] {c['text']}" for i, c in enumerate(top))
        messages = [
            {"role": "system", "content": (
                "You are a clinical evidence extraction assistant for a doctor-review tool. "
                "Using ONLY the provided note excerpts, state the most critical findings, "
                "risks, and recommended follow-up in 1-3 sentences. Cite excerpt numbers like "
                "[1]. If the excerpts do not support a finding, say so. Do not invent facts. "
                "This is decision support for clinician review, not a diagnosis.")},
            {"role": "user", "content": f"NOTE EXCERPTS:\n{context}\n\nQUESTION: {query}"},
        ]
        try:
            critical = azure_client.chat(messages, temperature=0.1, max_tokens=300).strip()
        except Exception as e:  # never let a RAG hiccup break the pipeline
            print(f"AzureRAG synthesis failed, using excerpt fallback: {e}")
            critical = top[0]["text"][:300] if top else "No critical findings extracted."

        return {
            "source": f"asclepius_notes.json ({self.name})",
            "raw_text_snippet": full_text,
            "critical_findings": critical,
            "citations": top,
            "backend": self.name,
        }
