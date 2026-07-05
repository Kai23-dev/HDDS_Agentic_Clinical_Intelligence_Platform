"""
Shared Azure Text Analytics for Health helper.

Single place that turns raw clinical text into structured medical entities
(diagnoses, medications, symptoms, age, gender). Env-guarded and fully optional:
returns None when Azure Language credentials are absent so every caller can fall
back gracefully.

Requires:  AZURE_LANGUAGE_ENDPOINT, AZURE_LANGUAGE_KEY
"""

import os
from typing import List, Dict, Optional


def is_configured() -> bool:
    return bool(os.getenv("AZURE_LANGUAGE_ENDPOINT") and os.getenv("AZURE_LANGUAGE_KEY"))


def extract_entities_from_text(text: str) -> Optional[List[Dict]]:
    """
    Return [{"text", "category", "confidence_score"}, ...] for one document,
    or None if Azure is not configured / the call fails (caller should fall back).
    """
    if not is_configured() or not text or not text.strip():
        return None
    try:
        from agents.azure_health_nlp import extract_health_insights
        results = extract_health_insights([text[:5000]])  # API caps document size
        return results[0] if results else []
    except Exception as e:
        print(f"Azure Health NLP error: {e}. Falling back to local extraction.")
        return None
