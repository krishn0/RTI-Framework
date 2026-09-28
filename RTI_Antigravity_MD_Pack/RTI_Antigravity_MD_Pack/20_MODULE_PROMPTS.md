# Copy-Paste Module Prompts for Antigravity

Use one prompt at a time. Do not ask the coding agent to implement the whole system in one run.

## Prompt A — Database Intelligence Layer
Read `00_MASTER_README.md`, `03_ANTIGRAVITY_EXECUTION_RULES.md`, and `04_DATABASE_AND_MIGRATIONS.md`. Inspect the existing SQLAlchemy models/migrations. Implement only the new intelligence-layer tables and migrations required for investigations, chunks, claims, sources, gaps, contradictions, events, RTI applications and RTI responses. Preserve all existing models and APIs. Add schema tests and verify migration against a copy/new instance of the existing database. Report exactly what changed.

## Prompt B — Embeddings + pgvector
Read `05_RAG_VECTOR_DB.md`. Inspect current document/page extraction and search code. Implement idempotent chunk creation, embedding generation and pgvector storage. Preserve page/version provenance. Do not replace the existing keyword search. Add tests for reprocessing, duplicate suppression and page linkage.

## Prompt C — Hybrid RAG
Using the existing search plus pgvector, build a hybrid evidence retrieval service. It must support metadata filtering, return a stable evidence-pack schema, preserve document/page/version/source URL, deduplicate repeated versions, and work without invoking the LLM. Add retrieval tests using fixtures.

## Prompt D — Knowledge Layer
Read `06_KNOWLEDGE_GRAPH.md`. Implement the MVP graph using PostgreSQL relationships, not Neo4j unless explicitly requested. Add entity/relationship APIs and temporal fields. Do not merge ambiguous entities. Add tests for project->tender->contractor traversal.

## Prompt E — Planner + Agents
Read `07_AGENT_ORCHESTRATION.md`. Implement Pydantic input/output contracts first, then the investigation planner, router and core agents. Ensure each claim contains source references and initial status PROPOSED. Bound agent calls and persist agent run logs. Add mocked LLM tests.

## Prompt F — Evidence Reasoning
Read `08_EVIDENCE_REASONING.md`. Implement claim verification, contradiction detection, expected-evidence comparison and gap detection. Keep different financial concepts separate. Do not use the LLM for deterministic comparisons that can be implemented in code. Add unit tests for temporal revisions and false contradiction prevention.

## Prompt G — RTI Engine
Read `09_RTI_ENGINE.md`. Implement authority resolution, gap-to-question conversion, duplicate suppression and RTI draft creation. Every generated question must link back to an evidence gap. Make drafts editable and do not implement automatic legal submission.

## Prompt H — RTI Response Loop
Read `10_RTI_RESPONSE_LOOP.md`. Reuse the existing document extraction pipeline for uploaded official responses. Implement question-response alignment, completeness classifications, new claim extraction with provenance, gap-state updates and targeted re-investigation. Add an end-to-end test.

## Prompt I — Intelligence APIs
Read `11_API_CONTRACTS.md`. Expose the implemented intelligence modules through a separate namespace. Use Pydantic response schemas and stable error objects. Do not alter existing public/admin endpoints.

## Prompt J — Dashboard
Read `12_FRONTEND_DASHBOARD.md`. Inspect current React routing/design system and extend it. Implement investigation, evidence, known/missing, digital twin, timeline, money trail, contradiction, RTI draft and response-analysis screens. Handle loading, empty, partial and error states. Do not duplicate backend logic.

## Prompt K — Full QA
Read `13_TESTING_QA.md` and `18_DEFINITION_OF_DONE.md`. Run the complete backend/frontend test suite, add missing integration tests, verify existing CoreScapper routes, test migrations, and execute the golden investigation flow. Fix only reproducible defects and report unresolved issues precisely.
