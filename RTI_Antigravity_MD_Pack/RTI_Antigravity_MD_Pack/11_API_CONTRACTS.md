# API Contracts for Intelligence Layer

## General Rules
- prefix new APIs with `/api/intelligence` or another isolated namespace
- do not break existing `/api/search`, `/api/documents`, `/api/sources`, scraper or admin endpoints
- all responses must use Pydantic schemas
- return stable IDs for investigation, claim, evidence and RTI objects

## Proposed Endpoints

### Investigations
`POST /api/intelligence/investigations`
```json
{ "query": "..." }
```
Returns investigation ID and initial state.

`GET /api/intelligence/investigations/{id}`
Returns overall status, plan and summary.

`POST /api/intelligence/investigations/{id}/run`
Runs or resumes investigation.

### Evidence
`GET /api/intelligence/investigations/{id}/evidence`

`GET /api/intelligence/investigations/{id}/claims`

`GET /api/intelligence/investigations/{id}/gaps`

`GET /api/intelligence/investigations/{id}/contradictions`

### Project Intelligence
`GET /api/intelligence/projects/{id}/timeline`

`GET /api/intelligence/projects/{id}/money-trail`

`GET /api/intelligence/projects/{id}/profile`

### RTI
`POST /api/intelligence/investigations/{id}/rti-draft`

`GET /api/intelligence/rti/{rti_id}`

### RTI Response
`POST /api/intelligence/rti/{rti_id}/response`
Multipart upload or document reference.

`GET /api/intelligence/rti/{rti_id}/response-analysis`

## Standard Error Shape
```json
{
  "error": {
    "code": "validation_error",
    "message": "...",
    "details": {}
  }
}
```

## API Versioning
If contracts become unstable, use `/api/v1/intelligence` before public deployment.
