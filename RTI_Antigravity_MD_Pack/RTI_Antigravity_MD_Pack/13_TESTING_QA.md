# Testing and Quality Assurance Plan

## Philosophy
Do not rely on "it worked once". The MVP must have repeatable tests.

## Test Layers

### Unit Tests
Test:
- chunking
- normalization
- hash/version helper integration where reused
- claim comparison
- financial concept normalization
- gap-template comparison
- RTI question deduplication
- response classification helpers

### Database Tests
- migrations upgrade successfully
- foreign-key integrity
- duplicate prevention
- investigation cascade behavior is intentional

### Retrieval Tests
Create a small fixture set where expected document/page is known.
Measure:
- top-k retrieval success
- page accuracy
- duplicate suppression

### Agent Contract Tests
Mock the LLM and test:
- valid JSON
- invalid JSON retry
- missing required field rejection
- empty evidence behavior
- contradiction behavior

### Integration Tests
1. create investigation
2. retrieve evidence
3. run agents
4. create claims
5. verify claims
6. create gaps
7. generate RTI
8. upload response
9. update gap state

### Regression Tests
Existing CoreScapper endpoints must remain functional:
- search
- document view
- news view
- YouTube view
- source management
- scraper execution

## Golden Test Case
Maintain at least one fully curated project case with:
- known supporting documents
- expected claims
- known missing record
- expected RTI question
- sample RTI response

## Quality Gates
No merge if:
- tests fail
- migration fails
- API schema differs unintentionally
- unsupported claim is stored without evidence
- existing search/scraper regression fails

## Research Metrics
- Retrieval Recall@K
- Citation Accuracy
- Claim Support Rate
- Contradiction Detection Precision
- Gap Detection Precision/Recall
- RTI Question Relevance (human-rated)
