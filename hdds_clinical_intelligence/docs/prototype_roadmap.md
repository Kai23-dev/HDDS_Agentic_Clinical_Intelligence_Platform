# Prototype Roadmap

## Phase 1: Foundation (Current)
- [x] Create project folder structure
- [x] Build synthetic patient profile (JSON)
- [x] Implement 6 rule-based agents
- [x] Build runner script (`run_hdds_prototype.py`)
- [x] Generate `ai_medical_insights.json` output
- [x] Add responsible AI disclaimers

## Phase 2: Enhanced Data
- [ ] Integrate Synthea CSV data extraction
- [ ] Build extraction pipeline to convert CSV → structured JSON
- [ ] Support multiple patient profiles
- [ ] Add sample clinical notes (unstructured text)

## Phase 3: NLP Extraction
- [ ] Add optional Azure Health NLP integration
- [ ] Extract entities from clinical notes (conditions, medications, labs)
- [ ] Map extracted entities to structured format

## Phase 4: Dashboard
- [ ] Build Streamlit or Flask dashboard
- [ ] Visualize agent outputs and risk levels
- [ ] Interactive patient selector
- [ ] Export reports as PDF

## Phase 5: Advanced Agents
- [ ] Upgrade from rule-based to ML-based agents
- [ ] Add drug interaction checking agent
- [ ] Add care gap analysis agent
- [ ] Integrate FHIR-compatible data formats
