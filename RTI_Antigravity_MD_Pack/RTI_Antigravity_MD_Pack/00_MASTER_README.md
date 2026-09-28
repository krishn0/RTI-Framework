# RTI Agentic Framework — Antigravity Master Build Pack

## Purpose
This folder is the authoritative implementation guide for extending the existing **CoreScapper** platform into the full **Closed-Loop Multi-Agent RTI Intelligence Framework**.

The existing scraper/collector system is considered **implemented and stable**. Do **not** rebuild, replace, or broadly refactor it unless a new intelligence module requires a small, isolated integration point.

## Existing Baseline (Do Not Rebuild)
CoreScapper already provides:
- FastAPI backend
- React + Vite frontend
- SQLAlchemy models with PostgreSQL production support and SQLite local fallback
- Government PDF ingestion with PyMuPDF
- News ingestion with BeautifulSoup
- Official YouTube transcript ingestion
- SHA-256 document versioning and deduplication
- Search, filtering, page-level PDF matching, transcript timestamp matching
- Source registry and source analyzer
- APScheduler-based recurring jobs
- Admin console, scraper controls, logs, source health
- robots.txt compliance, crawl delays, SSRF protection
- Docker / Docker Compose support

## Remaining Objective
Build this pipeline on top of the existing system:

```text
User Query
  -> Query Understanding
  -> Evidence Retrieval (RAG + metadata + graph)
  -> Investigation Planner
  -> Multi-Agent Analysis
  -> Evidence Verification
  -> Contradiction Detection
  -> Evidence-Gap Detection
  -> RTI Generation
  -> RTI Response Analysis
  -> Knowledge Update
  -> Re-investigation
  -> Citizen Transparency Dashboard
```

## Mandatory Implementation Order
1. Database migrations for intelligence layer
2. Embedding/chunk pipeline
3. pgvector retrieval
4. Hybrid RAG service
5. Evidence/claim model
6. Investigation planner + agent contracts
7. Core agents
8. Verification + contradiction + gap engines
9. RTI generation
10. RTI response loop
11. APIs
12. Dashboard integration
13. End-to-end tests
14. Deployment hardening
15. Research evaluation

## Non-Negotiable Rules
- Never fabricate government facts.
- Every factual finding must point to evidence.
- Store source URL, document ID, page/timestamp, document version, and retrieval time where available.
- If evidence is missing, output `MISSING`, not a guess.
- If two records conflict, output `CONTRADICTED` or `UNRESOLVED`, not a forced answer.
- Never label an anomaly as fraud/corruption without explicit authoritative evidence.
- Preserve original documents and versions.
- Avoid destructive schema changes.
- All new APIs must be backward-compatible with existing public/admin APIs.
- All new modules require tests and acceptance criteria before integration.

## Recommended Reading Order
Read these files in order:
1. `01_PROJECT_CONTEXT.md`
2. `02_MASTER_ARCHITECTURE.md`
3. `03_ANTIGRAVITY_EXECUTION_RULES.md`
4. `04_DATABASE_AND_MIGRATIONS.md`
5. `05_RAG_VECTOR_DB.md`
6. `06_KNOWLEDGE_GRAPH.md`
7. `07_AGENT_ORCHESTRATION.md`
8. `08_EVIDENCE_REASONING.md`
9. `09_RTI_ENGINE.md`
10. `10_RTI_RESPONSE_LOOP.md`
11. `11_API_CONTRACTS.md`
12. `12_FRONTEND_DASHBOARD.md`
13. `13_TESTING_QA.md`
14. `14_SECURITY_AND_SAFETY.md`
15. `15_DEVOPS_DEPLOYMENT.md`
16. `16_RESEARCH_EVALUATION.md`
17. `17_TEAM_OWNERSHIP.md`
18. `18_DEFINITION_OF_DONE.md`

## Important Reality Check
No prompt or Markdown file can guarantee zero bugs. This pack is designed to **minimize mistakes** by forcing clear contracts, migrations, validation, tests, traceability, and staged integration.
