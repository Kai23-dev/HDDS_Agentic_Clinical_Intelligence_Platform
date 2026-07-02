# Azure Health NLP — Optional Integration (Future)

## Overview

Azure Health NLP (Text Analytics for Health) can be used in future phases to extract medical entities from unstructured clinical notes.

## Capabilities

- **Named Entity Recognition**: Conditions, medications, dosages, lab values
- **Relation Extraction**: Links between medications and conditions
- **Assertion Detection**: Negation, conditional, family history
- **ICD/SNOMED Linking**: Map entities to standard medical codes

## Integration Plan

1. Add clinical notes to `data/sample_notes/`
2. Use Azure Text Analytics for Health API to extract entities
3. Map extracted entities to the existing `patient_profile.json` format
4. Feed enriched data through the agent pipeline

## Prerequisites

- Azure subscription with Cognitive Services
- Text Analytics for Health endpoint and API key
- `azure-ai-textanalytics` Python package

## Note

This is **not implemented** in the current prototype. The current version uses pre-structured synthetic JSON data and requires no external APIs or packages.
