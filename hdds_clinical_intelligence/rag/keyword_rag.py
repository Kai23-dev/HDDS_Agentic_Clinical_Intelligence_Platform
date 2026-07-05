"""
Keyword RAG backend -- offline fallback.

No API keys, no embeddings. This is the original prototype behavior, preserved so
the platform still runs on a laptop with no Azure/Gemini access. It is NOT a real
RAG system; it does simple keyword matching over the notes.
"""

from typing import List, Dict, Any

from rag.base import BaseRAGSystem
from rag.notes_loader import load_notes_by_patient


class KeywordRAGSystem(BaseRAGSystem):
    name = "keyword-fallback"

    def __init__(self):
        self.notes_db = load_notes_by_patient()

    def retrieve(self, patient_id: str, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        notes = self.notes_db.get(patient_id, [])
        q_terms = {t for t in query.lower().split() if len(t) > 3}
        scored = []
        for n in notes:
            text = n.get("text", "")
            overlap = sum(1 for t in q_terms if t in text.lower())
            if overlap:
                scored.append({"text": text, "score": float(overlap), "source": "asclepius_notes.json"})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def extract_information(self, patient_id: str, query_type: str = "all") -> Any:
        patient_notes = self.notes_db.get(patient_id, [])
        if not patient_notes:
            return "No unstructured clinical notes available."

        full_text = " ".join(n["text"] for n in patient_notes)
        lowered = full_text.lower()

        if "cardiology" in lowered or "infarction" in lowered:
            critical = ("High risk of cardiac event. Cardiology follow-up explicitly "
                        "recommended in notes.")
        elif "ketoacidosis" in lowered or "kidney" in lowered:
            critical = ("Patient treated for DKA. Strict glucose monitoring and nephrology "
                        "follow-up noted.")
        else:
            critical = "No critical unstructured findings extracted."

        return {
            "source": f"asclepius_notes.json ({self.name})",
            "raw_text_snippet": full_text,
            "critical_findings": critical,
            "backend": self.name,
        }
