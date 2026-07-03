import sys
sys.path.insert(0, 'hdds_clinical_intelligence')
import api
from api import ChatRequest

req = ChatRequest(patient_id="SYNTH-001", question="hello")
try:
    print(api.chat_with_patient(req, "mock-jwt-token-doctor@ey.com-doctor"))
except Exception as e:
    import traceback
    traceback.print_exc()
