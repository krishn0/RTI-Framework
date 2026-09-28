# Definition of Done — Project Completion Checklist

## Data / Existing CoreScapper
- [x] public-source scraping exists
- [x] PDF extraction exists
- [x] document hashing/versioning exists
- [x] news ingestion exists
- [x] YouTube transcript ingestion exists
- [x] source scheduler/admin exists
- [x] public search exists

## RAG
- [ ] document chunks stored
- [ ] embeddings generated
- [ ] pgvector enabled
- [ ] hybrid retrieval works
- [ ] page/source provenance preserved

## Knowledge
- [ ] entity types defined
- [ ] relationships stored
- [ ] project profile query works
- [ ] temporal values supported

## Agents
- [ ] planner works
- [ ] router works
- [ ] Government Data Agent works
- [ ] Tender + Budget Agent works
- [ ] Audit + Timeline Agent works
- [ ] Knowledge/Evidence Agent works
- [ ] structured validation enforced

## Evidence Reasoning
- [ ] claims stored with sources
- [ ] verification statuses work
- [ ] contradictions detected
- [ ] temporal revisions handled
- [ ] expected evidence templates work
- [ ] missing records detected

## RTI
- [ ] authority resolver works
- [ ] gap-driven questions work
- [ ] duplicate suppression works
- [ ] editable RTI draft produced

## Response Loop
- [ ] response upload works
- [ ] response text extraction works
- [ ] question-response alignment works
- [ ] completeness status works
- [ ] new facts stored with provenance
- [ ] gap states update
- [ ] affected investigation re-runs

## Frontend
- [ ] investigation screen
- [ ] progress screen
- [ ] evidence report
- [ ] known/missing view
- [ ] digital twin
- [ ] timeline
- [ ] money trail
- [ ] contradiction view
- [ ] RTI editor
- [ ] response analysis

## Quality
- [ ] existing scraper/search regression tests pass
- [ ] intelligence unit tests pass
- [ ] end-to-end golden case passes
- [ ] migration tested from existing DB
- [ ] no secret in repository
- [ ] no unsupported factual claim without evidence

## Research
- [ ] evaluation dataset prepared
- [ ] retrieval metrics measured
- [ ] citation/claim metrics measured
- [ ] gap/contradiction metrics measured
- [ ] architecture figure finalized
- [ ] limitations documented

## Demo
- [ ] one real/public-data case runs from query to evidence
- [ ] missing record is detected
- [ ] RTI draft is generated
- [ ] sample official response is analyzed
- [ ] knowledge state visibly updates
