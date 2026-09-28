# Knowledge Graph Specification

## Goal
Represent relationships that vector search alone cannot answer reliably.

## MVP Strategy
Implement graph relationships in PostgreSQL first. Neo4j is optional after MVP stabilization.

## Canonical Entity Types
- Project
- Department
- PublicAuthority
- Tender
- Contractor
- Scheme
- Document
- DocumentVersion
- Payment / FinancialEvent
- AuditFinding
- Location
- RTIApplication
- RTIResponse

## Canonical Relationship Types
- `ISSUED_BY`
- `AWARDED_TO`
- `FUNDED_BY`
- `PART_OF_SCHEME`
- `LOCATED_IN`
- `MENTIONED_IN`
- `SUPPORTED_BY`
- `SUPERSEDES`
- `AUDITED_BY`
- `PAID_TO`
- `RESPONDS_TO`
- `REQUESTS_RECORD_FROM`

## Temporal Properties
Relationships and claims should support:
- `valid_from`
- `valid_to`
- `observed_at`

## Entity Resolution Rules
Never merge two entities solely because their names are similar.
Use available identifiers and context such as:
- tender number
- registration/company number if public
- department code
- project code
- location
- document references

Unknown entity matches must remain separate until confidence is sufficient.

## Example Query
"Show all projects awarded to Contractor X that had a deadline extension."

Required graph path:
```text
Contractor <-AWARDED_TO- Tender -> Project -> ProjectEvent(EXTENSION)
```

## Knowledge Agent Responsibilities
- resolve entities
- attach claims to entities
- attach documents to claims
- find related evidence
- traverse project/tender/contractor links
- return provenance with every relationship

## Acceptance Criteria
- project profile can list department, tender, contractor and source documents
- old and revised deadlines can coexist temporally
- entity relation APIs are deterministic and do not require the LLM for simple traversal
