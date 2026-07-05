"""
Shared loader for the unstructured Asclepius clinical notes.

Both the keyword and Azure RAG backends index the same source file so they stay
comparable. Notes are grouped by patient_id.
"""

import os
import json
from typing import Dict, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES_PATH = os.path.join(BASE_DIR, "data", "raw", "asclepius_notes.json")


def load_notes_by_patient() -> Dict[str, List[dict]]:
    """Return {patient_id: [note, ...]}; empty dict if the source file is missing."""
    notes_db: Dict[str, List[dict]] = {}
    if not os.path.exists(NOTES_PATH):
        print("Warning: Asclepius notes not found. Run data_ingestion/asclepius_ingest.py first.")
        return notes_db

    with open(NOTES_PATH, "r", encoding="utf-8") as f:
        notes = json.load(f)

    for note in notes:
        pid = note.get("patient_id")
        notes_db.setdefault(pid, []).append(note)
    return notes_db
