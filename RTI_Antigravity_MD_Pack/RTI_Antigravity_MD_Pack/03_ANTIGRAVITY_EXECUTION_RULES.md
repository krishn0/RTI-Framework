# Antigravity Execution Rules

## Purpose
These instructions are for any coding agent working on this repository.

## Before Changing Code
1. Read the repository structure.
2. Identify existing modules relevant to the task.
3. Do not create duplicate functionality.
4. Inspect current models and APIs before proposing schema/API changes.
5. Determine backward-compatibility impact.
6. Write a short implementation plan in the task notes.

## Change Discipline
- Prefer small changes over large rewrites.
- One module per change set where practical.
- Do not rename existing public endpoints unless explicitly approved.
- Do not delete existing database columns/tables.
- Add migrations for all schema changes.
- Add config through environment variables instead of hardcoding secrets.
- New external integrations must be behind service interfaces.

## Required Output Contract for Every Task
Before coding, define:
- inputs
- outputs
- database tables touched
- APIs touched
- error behavior
- tests required
- rollback path

## Coding Standards
### Python
- Python 3.10+
- type hints on public functions
- Pydantic schemas for request/response boundaries
- SQLAlchemy 2.x patterns
- explicit exceptions; no bare `except`
- structured logging
- idempotent background work where possible

### React
- functional components
- isolate API logic in API/service layer
- loading/error/empty states required
- do not assume backend fields exist; handle optional fields
- avoid duplicating backend business logic in UI

## AI/LLM Rules
- Require structured JSON outputs validated by Pydantic.
- Never trust raw LLM text as database truth.
- Never persist an extracted claim without source linkage.
- Retry malformed structured output at most a bounded number of times.
- Treat model output as `PROPOSED` until evidence verifier confirms it.

## Database Rules
- migrations are mandatory
- unique constraints for stable identifiers
- indexes on foreign keys and commonly filtered fields
- no destructive migration in MVP
- maintain document version provenance

## Error Handling
Every service must return or raise a typed failure category:
- validation_error
- not_found
- dependency_error
- retrieval_error
- model_error
- database_error
- unsupported_input

## Done Means
A task is not done when code compiles. It is done only when:
- tests pass
- API contract is validated
- existing behavior still works
- errors are handled
- logging exists
- acceptance criteria are met
- README/module notes are updated
