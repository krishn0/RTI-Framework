# Team Ownership and Handoff Contracts

## Shibu — AI / RAG / Knowledge Layer
Owns:
- embeddings
- pgvector
- hybrid RAG
- knowledge/graph model implementation
- investigation planner
- agent router
- Government Data Agent
- Tender + Budget Agent
- Audit + Timeline Agent
- Knowledge/Evidence Agent

Handoff to Yash:
- validated evidence pack schema
- normalized agent findings schema

Handoff to Krishna:
- investigation status API shape
- agent result API shape

## Pranali — RTI Engine and Response Intelligence
Owns:
- RTI schema
- authority resolver
- gap-to-question generator
- question deduplication
- RTI draft generation
- response upload integration
- question-response alignment
- completeness classification
- new-fact extraction payload

Handoff to Yash/CS1G:
- newly extracted response facts
- response classification schema

Handoff to Krishna:
- RTI draft and response analysis APIs

## Yash — Evidence Reasoning Backend
Owns:
- evidence claim models
- claim source linkage
- contradiction detection
- expected evidence model
- gap detection
- project timeline
- money trail
- evidence APIs

Handoff to Pranali:
- gap objects
- authority hints

Handoff to Krishna:
- claims/gaps/contradictions/timeline/money-trail APIs

## CS1G — Reliability, Integration and Research Support
Owns:
- investigation session model
- agent run logging
- error/retry handling
- security validation
- integration tests
- research ground-truth dataset
- evaluation metrics
- technical docs

## Krishna — Dashboard and Final Integration
Owns:
- investigation UI
- progress UI
- evidence report
- known vs missing
- project digital twin
- timeline
- money trail
- contradiction view
- RTI editor/export
- response analysis UI
- full API integration
- deployment integration
- research screenshots/figures/demo narrative

## Merge Rule
No teammate should silently change another person's public contract. Contract changes must be reflected in the relevant MD file and communicated before merging.
