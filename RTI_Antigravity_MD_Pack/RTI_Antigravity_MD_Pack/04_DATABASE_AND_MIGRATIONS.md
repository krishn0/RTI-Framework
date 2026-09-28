# Database and Migration Specification

## Objective
Extend the current SQLAlchemy database without breaking existing source/document/news/video models.

## New Core Tables

### `document_chunks`
Purpose: retrievable semantic units.

Suggested fields:
- `id`
- `document_id`
- `document_version_id` nullable if current schema lacks versions table
- `page_number` nullable
- `chunk_index`
- `text`
- `language`
- `token_count`
- `embedding` vector
- `metadata_json`
- `created_at`

Constraints:
- unique `(document_id, document_version_id, page_number, chunk_index)` where possible

### `investigations`
- `id`
- `query`
- `normalized_query`
- `status`
- `user_id` nullable for MVP
- `created_at`
- `updated_at`

### `investigation_steps`
- `id`
- `investigation_id`
- `step_type`
- `agent_name`
- `status`
- `input_json`
- `output_json`
- `started_at`
- `finished_at`
- `error_message`

### `evidence_claims`
- `id`
- `investigation_id`
- `subject_entity_type`
- `subject_entity_id` nullable
- `subject_text`
- `predicate`
- `value_text`
- `normalized_value_json`
- `valid_from` nullable
- `valid_to` nullable
- `status`
- `confidence_label`
- `created_at`

Allowed status values:
- `PROPOSED`
- `SUPPORTED`
- `VERIFIED`
- `PARTIAL`
- `CONTRADICTED`
- `MISSING`
- `STALE`

### `claim_sources`
- `id`
- `claim_id`
- `document_id`
- `document_version_id` nullable
- `page_number` nullable
- `timestamp_seconds` nullable
- `source_url`
- `quoted_excerpt` short and bounded
- `retrieval_score` nullable
- `source_authority_score` nullable

### `evidence_gaps`
- `id`
- `investigation_id`
- `project_id` nullable
- `gap_type`
- `expected_record_type`
- `description`
- `status`
- `responsible_authority_id` nullable
- `created_at`

### `contradictions`
- `id`
- `investigation_id`
- `claim_a_id`
- `claim_b_id`
- `contradiction_type`
- `resolution_status`
- `resolution_note`

### `project_events`
- `id`
- `project_id`
- `event_type`
- `event_date`
- `value_json`
- `source_claim_id`

### `financial_events`
- `id`
- `project_id`
- `event_type` (`SANCTION`, `ESTIMATE`, `AWARD`, `RELEASE`, `PAYMENT`, `EXPENDITURE`)
- `amount`
- `currency`
- `event_date`
- `source_claim_id`

### `rti_applications`
- `id`
- `investigation_id`
- `authority_name`
- `authority_id` nullable
- `subject`
- `draft_text`
- `status`
- `created_at`

### `rti_questions`
- `id`
- `rti_application_id`
- `sequence_no`
- `gap_id` nullable
- `question_text`
- `requested_record_type`

### `rti_responses`
- `id`
- `rti_application_id`
- `document_id` nullable
- `received_date` nullable
- `raw_text`
- `created_at`

### `rti_response_items`
- `id`
- `rti_response_id`
- `rti_question_id`
- `classification`
- `answer_text`
- `evidence_json`

Allowed classifications:
- `ANSWERED`
- `PARTIAL`
- `NOT_ANSWERED`
- `DOCUMENT_ATTACHED`
- `TRANSFERRED`
- `EXEMPTION_CITED`
- `UNCLEAR`

## Migration Rules
- never drop current tables
- add indexes for investigation/status/date/foreign-key lookups
- migration must work on PostgreSQL
- SQLite local fallback may skip pgvector-specific functionality with a clear feature flag

## Environment Variables
Recommended:
```env
DATABASE_URL=
VECTOR_ENABLED=true
EMBEDDING_MODEL=
EMBEDDING_DIMENSION=
LLM_PROVIDER=
LLM_MODEL=
```
