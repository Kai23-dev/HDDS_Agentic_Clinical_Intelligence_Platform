from fpdf import FPDF

class MedicalPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "Asclepius Health Systems - Patient Medical Record", 0, 1, "C")
        self.ln(5)

pdf = MedicalPDF()
pdf.add_page()
pdf.set_font("Arial", size=11)

messy_text = """
PATIENT ID: SYNTH-001
NAME: John Doe
DOB: 15-Mar-1968
ENCOUNTER DATE: 2026-07-02
ATTENDING PHYSICIAN: Dr. Smith, MD

CHIEF COMPLAINT:
Patient presents to the ED with acute shortness of breath and chest tightness.

HISTORY OF PRESENT ILLNESS:
The patient is a 58-year-old male with a known history of Type 2 Diabetes Mellitus and Hypertension. He states the chest tightness began approximately 4 hours ago. He took his normal dose of Lisinopril this morning. He denies any recent travel or sick contacts.

VITAL SIGNS:
BP: 145/92 mmHg
HR: 88 bpm
Resp: 22 breaths/min
Temp: 98.6 F
O2 Sat: 94% on room air

LABORATORY RESULTS (Flagged):
- HbA1c: 8.5% (HIGH - reference < 5.7%)
- Glucose: 195 mg/dL (HIGH)
- eGFR: 55 mL/min (LOW)

CURRENT MEDICATIONS:
1. Metformin 1000mg BID
2. Lisinopril 20mg daily
3. Atorvastatin 40mg daily
4. Aspirin 81mg daily
5. Amlodipine 5mg daily

ASSESSMENT & PLAN:
1. Acute exacerbation of hypertension, possibly secondary to medication non-compliance or stress. Will monitor.
2. Uncontrolled Type 2 Diabetes (HbA1c 8.5%). We will adjust Metformin dosage and recommend strict endocrinology follow-up. 
3. Note: Patient is currently on 5 active medications (Polypharmacy flag). Care team should review for potential drug-drug interactions.

DISPOSITION:
Admit for observation. Follow up with Cardiology in 2 weeks.
"""

for line in messy_text.split('\n'):
    pdf.multi_cell(0, 6, line)

pdf.output("dummy_medical_record.pdf")
