# 7-Day Execution Plan

This is an aggressive MVP schedule. Parallel work by team members is assumed.

## Day 1 — Contracts + Database
### Shibu
- embedding service interface
- pgvector setup
- chunk model integration

### Yash
- claims, claim_sources, gaps, contradictions, project_events, financial_events

### Pranali
- RTI application/question/response schemas

### CS1G
- investigation + investigation_steps models
- test harness

### Krishna
- dashboard route skeleton + API service interfaces

### Exit Gate
Migrations run, frontend still builds, existing CoreScapper routes work.

## Day 2 — Retrieval + Evidence
### Shibu
- chunking/embedding pipeline
- vector search
- hybrid evidence pack

### Yash
- verification service skeleton
- expected-evidence templates

### Pranali
- authority resolver data/interface

### CS1G
- integration tests for investigation creation/retrieval

### Krishna
- investigation and progress UI

### Exit Gate
Known query retrieves correct document/page.

## Day 3 — Agents
### Shibu
- planner
- router
- Government Data Agent
- Tender + Budget Agent
- Knowledge Agent

### Yash
- claim persistence
- contradiction normalization

### Pranali
- gap-to-question engine

### Krishna
- evidence report + known/missing UI

### Exit Gate
Query -> evidence -> sourced claims works.

## Day 4 — Reasoning
### Shibu
- Audit + Timeline Agent
- agent stabilization

### Yash
- contradiction engine
- timeline
- money trail
- gap detector

### Pranali
- RTI draft + deduplication

### CS1G
- failure/retry/logging hardening

### Krishna
- timeline/money trail/contradiction UI

### Exit Gate
Claims split correctly into known/missing/contradicted.

## Day 5 — RTI Closed Loop
### Pranali
- response upload/parser alignment
- response completeness
- new-fact payload

### Shibu/Yash
- knowledge reintegration hooks

### CS1G
- closed-loop integration test

### Krishna
- RTI editor + response analysis UI

### Exit Gate
Gap -> RTI -> sample response -> updated gap state works.

## Day 6 — Full Integration + QA
- connect all APIs/UI
- golden scenario
- regression tests
- fix reproducible defects
- deployment configuration

## Day 7 — Research Demo + Freeze
- deploy
- run golden scenario from fresh session
- capture screenshots
- measure initial research metrics
- finalize architecture/methodology notes
- freeze MVP features

## Scope Cut Rule
If behind schedule, postpone:
- Neo4j
- advanced contractor network analytics
- media correlation
- map/geospatial analytics
- advanced appeal drafting

Never postpone:
- provenance
- RAG retrieval
- claim verification
- gap detection
- RTI draft
- response reintegration
- end-to-end test
