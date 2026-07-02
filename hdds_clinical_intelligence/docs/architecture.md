# Architecture Overview

## System Design

The HDDS Agentic Clinical Intelligence Platform follows a **sequential multi-agent pipeline** architecture where synthetic patient data flows through six specialized agents, each performing a distinct clinical analysis task.

## Data Flow

```
Input (JSON) → Agent Pipeline → Output (JSON)
```

### Layer 1: Data Ingestion
- Patient data is stored as structured JSON in `data/processed/`
- Future: Synthea CSV extraction and FHIR-compatible formats

### Layer 2: Agent Pipeline
Each agent is a standalone Python class with a `run()` method:

1. **Clinical Summary Agent** — Produces a patient overview
2. **Risk Assessment Agent** — Calculates risk score and classification
3. **Early Detection Agent** — Identifies abnormal values and monitoring gaps
4. **Recommendation Agent** — Drafts treatment/management recommendations
5. **Evidence Validation Agent** — Cross-references outputs with source data
6. **Follow-up Action Agent** — Generates prioritized action items

### Layer 3: Output Generation
- All agent outputs are combined into a single JSON file
- Metadata includes timestamp, version, and responsible AI disclaimer

## Design Principles

- **No external dependencies** — Python standard library only
- **Synthetic data only** — No real patient information
- **Traceable outputs** — Every assertion maps to source data
- **Clinician-in-the-loop** — All outputs are drafts requiring review
