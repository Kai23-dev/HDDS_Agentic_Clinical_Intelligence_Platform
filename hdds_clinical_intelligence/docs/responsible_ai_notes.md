# Responsible AI Notes

## Purpose

This document outlines the responsible AI practices followed in the HDDS Agentic Clinical Intelligence Platform prototype.

## Key Principles

### 1. Not a Diagnostic Tool
All outputs from this system are generated for **prototype purposes only** and are intended for **clinician review**. The system does not make final diagnoses or treatment decisions.

### 2. Synthetic Data Only
This prototype uses **only synthetic/sample healthcare data**. No real patient data, company data, client data, internal GDX details, secrets, or tokens are used.

### 3. Clinician-in-the-Loop
Every recommendation, risk assessment, and follow-up action is explicitly marked as a **draft requiring clinician review and approval**. The system is designed to assist, not replace, clinical judgment.

### 4. Evidence Traceability
The Evidence Validation Agent maps every clinical assertion back to its source data fields, ensuring transparency and auditability of the AI-generated insights.

### 5. Transparency
- All agent outputs include version information
- Risk scores include full score breakdowns
- Recommendations include their rationale

## Disclaimer (Included in All Outputs)

> "This output is generated for prototype purposes only and is intended for clinician review. It is not a final diagnosis or treatment decision."
