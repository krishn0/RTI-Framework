# Project Context and Boundaries

## Project Name
**RTI Agentic Framework / Public Accountability Intelligence System**

## Product Goal
Convert fragmented public information into a traceable evidence system that can:
1. answer a citizen's question using public records,
2. show exactly which documents support each finding,
3. detect contradictory or missing records,
4. generate targeted RTI questions only for unresolved information,
5. ingest the official RTI response,
6. update the project knowledge state,
7. re-run the investigation using the newly acquired evidence.

## Current Stable System
The repository already contains a working collector/search platform named **CoreScapper**.

### Existing Backend
Expected modules include:
- `app/database.py`
- `app/models.py`
- `app/schemas.py`
- `app/main.py`
- `app/ingestion.py`
- `app/search.py`
- `app/scheduler.py`
- `app/source_registry.py`
- `app/migrations.py`

### Existing Frontend
Expected modules include:
- `src/App.jsx`
- `src/public.jsx`
- `src/api.js`
- `src/index.css`
- `src/main.jsx`

## Scope Exclusion
Do not spend project time rewriting:
- government PDF scraper
- news scraper
- YouTube transcript scraper
- source discovery
- source scheduler
- SHA-256 versioning
- public search
- existing admin scraper console

Only modify existing scraper/search code when required to expose data needed by the intelligence layer.

## MVP Scope
The MVP must demonstrate one complete case:

```text
User asks about a public project
-> evidence is retrieved
-> agents extract project/tender/budget/timeline findings
-> claims are cross-checked
-> missing records are identified
-> RTI draft is generated
-> sample official response is uploaded
-> system aligns response to questions
-> new facts update the evidence state
-> dashboard reflects the update
```

## Primary Users
- Citizen
- Researcher / journalist / civic analyst
- System administrator

## System Principles
- Evidence first
- Human review before legal action
- Explainable outputs
- Source provenance
- Temporal awareness
- No unsupported accusations
- Modular agent design
- Backward compatibility
