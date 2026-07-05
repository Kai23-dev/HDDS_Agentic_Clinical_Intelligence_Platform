import os

class ChatbotAgent:
    """
    Simulates a conversational agent that answers clinical questions.
    Uses Google Gemini if GEMINI_API_KEY is present, otherwise falls back to local rules.
    """
    def run(self, question: str, patient_data: dict) -> str:

        # Shared context used by every LLM backend
        unstructured = patient_data.get("gtx_unstructured_insights", {})
        notes_text = unstructured.get("raw_text_snippet", "") if isinstance(unstructured, dict) else str(unstructured)
        meds = [m.get("DESCRIPTION", m.get("name", "")) for m in patient_data.get("medications", [])]
        conds = [c.get("condition", "") for c in patient_data.get("medical_history", []) if c.get("status") == "Active"]

        # 1. Prefer Azure OpenAI (company deployment target)
        try:
            from llm import azure_client
            if azure_client.is_configured():
                messages = [
                    {"role": "system", "content": (
                        "You are a clinical assistant for doctor review. Answer ONLY from the "
                        "patient data provided. If the data does not contain the answer, say so. "
                        "Do not give a final diagnosis; this is decision support.")},
                    {"role": "user", "content": (
                        f"PATIENT CONDITIONS: {', '.join(conds)}\n"
                        f"PATIENT MEDICATIONS: {', '.join(meds)}\n"
                        f"CLINICAL NOTES: {notes_text}\n\n"
                        f"DOCTOR QUESTION: {question}")},
                ]
                return azure_client.chat(messages, temperature=0.2)
        except Exception as e:
            print(f"Azure OpenAI chat error: {e}. Falling back to Gemini/local.")

        # 2. Try Gemini if API key is present
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                
                # Build context
                unstructured = patient_data.get("gtx_unstructured_insights", {}).get("raw_text_snippet", "")
                meds = [m.get("DESCRIPTION", "") for m in patient_data.get("medications", [])]
                conds = [c.get("condition", "") for c in patient_data.get("medical_history", []) if c.get("status") == "Active"]
                
                prompt = f"""
                You are a highly capable clinical assistant. Answer the doctor's question based ONLY on the following patient data.
                
                PATIENT CONDITIONS: {', '.join(conds)}
                PATIENT MEDICATIONS: {', '.join(meds)}
                CLINICAL NOTES: {unstructured}
                
                DOCTOR QUESTION: {question}
                """
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                return response.text
            except Exception as e:
                print(f"Gemini API Error: {e}. Falling back to local mock.")
                # Fall through to mock logic

        # 2. Local Mock Fallback Logic
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
        if "history" in q or "condition" in q or "disease" in q:
            cond_names = [c["condition"] for c in conditions if c["status"] == "Active"]
            if cond_names:
                return f"The patient has a history of: {', '.join(cond_names)}."
            return "No active conditions on file."

        return (
            "I could not find a specific answer in the patient's records. "
            "Please review the clinical summary for more details."
        )
