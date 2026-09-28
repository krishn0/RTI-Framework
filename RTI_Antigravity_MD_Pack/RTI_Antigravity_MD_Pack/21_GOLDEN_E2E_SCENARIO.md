# Golden End-to-End Scenario

## Purpose
Every build should be verified against one repeatable demonstration case.

## Scenario
A citizen asks about a public infrastructure project and wants to know:
- sanctioned amount
- tender/contract value
- contractor
- deadline
- current publicly documented status
- whether extension/payment/completion records are available

## Required System Behavior
1. Create investigation.
2. Planner decomposes the query.
3. RAG retrieves public records from existing CoreScapper data.
4. Agents create sourced claims.
5. Verifier marks supported claims.
6. Timeline identifies original/revised dates.
7. Money trail keeps sanction/award/release/expenditure separate.
8. Gap engine identifies at least one truly absent expected record in the curated fixture.
9. RTI engine generates a precise record request for that gap.
10. User uploads a prepared sample official response.
11. Response engine maps answer to RTI question.
12. New official fact is stored with page/source provenance.
13. Relevant gap state changes.
14. Affected timeline/money-trail/verification step reruns.
15. Dashboard shows updated result.

## Pass Criteria
- no unsupported claim
- all displayed claims have source links
- missing evidence is never invented
- response updates are auditable
- existing CoreScapper search still works
