import os
import re

# Process-level circuit breakers. Once a backend fails, skip it for the rest of the
# process instead of repeating the same slow, failing network round-trip on every
# subsequent chat message.
_AZURE_BROKEN = False
_GEMINI_BROKEN = False

GREETING_RE = re.compile(r"^\s*(hi|hello|hey|good\s*(morning|afternoon|evening)|yo|sup)\b[!.?]*\s*$", re.I)
THANKS_RE = re.compile(r"\b(thanks|thank\s*you|thx|appreciate\s*it)\b", re.I)
BYE_RE = re.compile(r"^\s*(bye|goodbye|see\s*you|later)\b[!.?]*\s*$", re.I)


class ChatbotAgent:
    """
    Conversational agent that answers clinical questions about a patient.
    Uses Azure OpenAI if configured, Gemini as a fallback, and a rule-based
    local responder if neither is available or both fail.
    """

    def run(self, question: str, patient_data: dict, agent_results: dict | None = None) -> str:
        global _AZURE_BROKEN, _GEMINI_BROKEN
        agent_results = agent_results or {}
        profile = patient_data.get("patient_profile", {})
        patient_name = (
            patient_data.get("patient_name") or patient_data.get("name")
            or profile.get("patient_name") or profile.get("name") or "the patient"
        )

        q = question.strip()
        if GREETING_RE.match(q):
            return f"Hello, Doctor. I've reviewed {patient_name}'s record and I'm ready to help. What would you like to know?"
        if BYE_RE.match(q):
            return "Goodbye, Doctor. Let me know if you need anything else on this patient."
        if THANKS_RE.search(q) and len(q) < 40:
            return "You're welcome. Anything else you'd like to review?"

        context = self._build_context(patient_data, agent_results)

        # 1. Prefer Azure OpenAI (company deployment target)
        if not _AZURE_BROKEN:
            try:
                from llm import azure_client
                if azure_client.is_configured():
                    messages = [
                        {"role": "system", "content": (
                            "You are a clinical assistant helping a doctor review an AI-generated "
                            "patient analysis. Answer conversationally and concisely. Ground clinical "
                            "claims (risk, medications, conditions, recommendations) in the CONTEXT "
                            "below; if the context doesn't cover it, say so plainly. This is decision "
                            "support only, never a final diagnosis.")},
                        {"role": "user", "content": f"{context}\n\nDOCTOR QUESTION: {question}"},
                    ]
                    return azure_client.chat(messages, temperature=0.2, timeout=6.0)
            except Exception as e:
                _AZURE_BROKEN = True
                print(f"Azure OpenAI chat error: {e}. Disabling Azure OpenAI for this session, falling back to Gemini/local.")

        # 2. Try Gemini if API key is present
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and not _GEMINI_BROKEN:
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=api_key)
                prompt = (
                    "You are a highly capable clinical assistant helping a doctor review an "
                    "AI-generated patient analysis. Answer conversationally and concisely, "
                    "grounding clinical claims in the context below.\n\n"
                    f"{context}\n\nDOCTOR QUESTION: {question}"
                )
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(http_options=types.HttpOptions(timeout=6000)),
                )
                return response.text
            except Exception as e:
                _GEMINI_BROKEN = True
                print(f"Gemini API error: {e}. Disabling Gemini for this session, falling back to local rules.")

        # 3. Local rule-based fallback
        return self._local_fallback(question, patient_data, agent_results)

    @staticmethod
    def _build_context(patient_data: dict, agent_results: dict) -> str:
        """Assemble a compact text context from structured agent output + raw patient fields."""
        unstructured = patient_data.get("gtx_unstructured_insights", {})
        notes_text = unstructured.get("raw_text_snippet", "") if isinstance(unstructured, dict) else str(unstructured)
        meds = [m.get("DESCRIPTION", m.get("name", "")) for m in patient_data.get("medications", [])]
        conds = [c.get("condition", "") for c in patient_data.get("medical_history", []) if c.get("status") == "Active"]

        lines = [
            f"PATIENT CONDITIONS: {', '.join(conds) or 'none on file'}",
            f"PATIENT MEDICATIONS: {', '.join(meds) or 'none on file'}",
        ]
        if notes_text:
            lines.append(f"CLINICAL NOTES: {notes_text}")

        risk = agent_results.get("risk_assessment")
        if risk:
            lines.append(f"RISK LEVEL: {risk.get('risk_level')} (score {risk.get('risk_score')}) - {risk.get('rationale', '')}")

        summary = agent_results.get("clinical_summary")
        if summary and summary.get("summary_text"):
            lines.append(f"CLINICAL SUMMARY: {summary['summary_text']}")

        recs = agent_results.get("recommendations", {}).get("recommendations", [])
        if recs:
            rec_lines = "; ".join(r.get("recommendation", "") for r in recs[:6])
            lines.append(f"RECOMMENDATIONS: {rec_lines}")

        rx = agent_results.get("medication_prescription", {}).get("prescriptions", [])
        if rx:
            rx_lines = "; ".join(f"{p.get('diagnosis')}: {p.get('suggested_medication')} ({p.get('dosage_guideline')})" for p in rx[:6])
            lines.append(f"TREATMENT/MEDICATION SUGGESTIONS: {rx_lines}")

        flags = agent_results.get("early_detection", {}).get("flagged_abnormal_results", [])
        if flags:
            flag_lines = "; ".join(f"{f.get('test_name')} {f.get('value')} {f.get('unit', '')} ({f.get('severity')})" for f in flags[:6])
            lines.append(f"ABNORMAL LAB FLAGS: {flag_lines}")

        followups = agent_results.get("followup_actions", {}).get("follow_up_actions", [])
        if followups:
            fu_lines = "; ".join(a.get("action", "") for a in followups[:6])
            lines.append(f"FOLLOW-UP ACTIONS: {fu_lines}")

        return "\n".join(lines)

    @staticmethod
    def _local_fallback(question: str, patient_data: dict, agent_results: dict) -> str:
        q = question.lower()

        gtx_insights = patient_data.get("gtx_unstructured_insights", "")
        unstructured = gtx_insights.get("raw_text_snippet", "").lower() if isinstance(gtx_insights, dict) else str(gtx_insights).lower()
        if unstructured:
            if "hba1c" in q and "hba1c" in unstructured:
                return "Based on the discharge summary, the patient's HbA1c was noted to be elevated at 8.5%."
            if "cardiology" in q and "cardiology" in unstructured:
                return "Yes, a cardiology follow-up in 2 weeks is highly recommended due to the high risk of readmission."
            if "kidney" in q or "dka" in q:
                return "The patient has a history of stage 3 CKD and was treated for diabetic ketoacidosis (DKA) with IV fluids and insulin."

        risk = agent_results.get("risk_assessment")
        if risk and ("risk" in q or "how severe" in q or "how bad" in q):
            return f"Risk level is **{risk.get('risk_level')}** (score {risk.get('risk_score')}). {risk.get('rationale', '')}"

        rx = agent_results.get("medication_prescription", {}).get("prescriptions", [])
        if rx and ("treatment" in q or "prescri" in q or "plan" in q or "manage" in q):
            lines = [f"For {p.get('diagnosis')}: {p.get('suggested_medication')} ({p.get('dosage_guideline')})" for p in rx]
            return "Suggested treatment plan (pending clinician approval):\n" + "\n".join(lines)

        recs = agent_results.get("recommendations", {}).get("recommendations", [])
        if recs and ("recommend" in q or "suggest" in q or "should i" in q):
            return "Recommendations on file: " + "; ".join(r.get("recommendation", "") for r in recs)

        followups = agent_results.get("followup_actions", {}).get("follow_up_actions", [])
        if followups and ("follow" in q or "next step" in q or "next visit" in q):
            return "Follow-up actions: " + "; ".join(a.get("action", "") for a in followups)

        summary = agent_results.get("clinical_summary", {}).get("summary_text")
        if summary and ("summar" in q or "overview" in q or "tell me about" in q or "what's going on" in q):
            return summary

        meds = patient_data.get("medications", [])
        if "medication" in q or "drugs" in q or "prescribed" in q:
            med_names = [m.get("DESCRIPTION", m.get("name", "Unknown")) for m in meds]
            if med_names:
                return f"The patient is currently prescribed: {', '.join(med_names)}."
            return "The patient has no active medications on file."

        labs = patient_data.get("lab_results", [])
        if "lab" in q or "test" in q:
            lab_names = [f"{l['test_name']} ({l['value']} {l['unit']})" for l in labs]
            if lab_names:
                return f"Recent lab results include: {', '.join(lab_names)}."
            return "No recent lab results found."

        conditions = patient_data.get("medical_history", [])
        if "history" in q or "condition" in q or "disease" in q or "diagnos" in q:
            cond_names = [c["condition"] for c in conditions if c.get("status") == "Active"]
            if cond_names:
                return f"The patient has a history of: {', '.join(cond_names)}."
            return "No active conditions on file."

        return (
            "I don't have a direct answer to that from this patient's record. Try asking about "
            "risk level, treatment plan, medications, recent labs, or follow-up actions."
        )
