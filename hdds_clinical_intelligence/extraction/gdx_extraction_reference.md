# GDX Extraction Reference (Future)

## Overview

This document is a placeholder reference for future GDX-style data extraction integration.

## Purpose

In a production HDDS system, data extraction from clinical sources (EHRs, lab systems, pharmacy systems) follows a structured pipeline:

1. **Raw data ingestion** — Data arrives in various formats (HL7, FHIR, CSV, PDF)
2. **Parsing & normalization** — Data is parsed into a common intermediate format
3. **Entity extraction** — Clinical entities are identified (conditions, meds, labs)
4. **Harmonization** — Entities are mapped to standard terminologies (ICD-10, SNOMED, LOINC, RxNorm)
5. **Validation** — Extracted data is validated against the extraction schema
6. **Loading** — Validated data is loaded into the structured patient profile format

## Current Prototype

The current prototype **skips extraction entirely** and uses pre-built synthetic JSON data. This reference documents how extraction would work in a full implementation.

## Note

No internal GDX details, proprietary processes, or confidential information are included in this document. This is a general reference only.
