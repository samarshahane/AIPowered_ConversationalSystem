# Verdant

Verdant is an AI Biodiversity Intelligence system. It takes the measurable state of a land parcel and returns scientifically grounded interventions to improve biodiversity. 

## Design Philosophy
**The LLM never decides what is feasible.** Feasibility is handled purely by deterministic Python rules evaluating numeric preconditions against user inputs.

## Features
- **Hard Rule Engine (Phase 4):** Evaluates preconditions exactly. No LLM hallucinations on feasibility.
- **Scorer & Resolver (Phase 4):** Resolves conflicts and scores via multi-metric optimization (coupled-effects).
- **RAG & Synthesis (Phase 6):** Grounds scientific explanations purely in real PDF chunks retrieved from ChromaDB.

## Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Seed the database with the intervention cards:
```bash
python scripts/seed_db.py
```

3. Build the knowledge index (add PDFs to data/corpus/ first):
```bash
python scripts/build_index.py
```

4. Run the API:
```bash
uvicorn src.main:app --reload
```

5. Run the Streamlit UI (in a separate terminal):
```bash
streamlit run app.py
```
