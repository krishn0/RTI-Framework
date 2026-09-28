# Evidence Reasoning, Contradiction and Gap Detection

## Evidence State Machine
Allowed states:
```text
PROPOSED -> SUPPORTED -> VERIFIED
     |          |
     |          -> CONTRADICTED
     -> PARTIAL
     -> MISSING
```

`STALE` can be applied when a fact was valid historically but superseded by newer official evidence.

## Cross-Source Verification
For each claim:
1. find direct supporting sources
2. find independent corroborating sources
3. check source dates
4. check document versions
5. search for incompatible claims
6. assign status

## Contradiction Detection
Two claims may be compared only if:
- same entity or confidently resolved entity
- same semantic property
- compatible units
- overlapping or comparable time scope

Example that is **not** automatically a contradiction:
- sanctioned amount ₹100 Cr
- awarded contract ₹82 Cr
- expenditure ₹70 Cr

These are different financial concepts.

Example candidate contradiction:
- completion deadline = March 2026
- completion deadline = September 2026

Then search for a valid extension/revision record before marking unresolved contradiction.

## Evidence Confidence
Use interpretable factors, not arbitrary model confidence:
- source authority
- directness
- corroboration
- recency
- contradiction penalty

Output labels:
- `STRONGLY_SUPPORTED`
- `SUPPORTED`
- `LIMITED_EVIDENCE`
- `INSUFFICIENT_EVIDENCE`

## Expected Evidence Model
For infrastructure project MVP, expected records can include:
- administrative approval
- financial sanction
- tender notice
- award/work order
- contractor information
- progress report
- payment/release records
- deadline extension orders
- completion certificate
- audit report where applicable

## Gap Detection Algorithm
```text
expected record schema
 + project/entity context
 + available evidence inventory
 -> missing expected records
 -> missing critical facts
 -> responsible authority candidate
```

## Gap Output
```json
{
  "gap_type": "MISSING_RECORD",
  "expected_record_type": "completion_certificate",
  "description": "No completion certificate was found in indexed official records.",
  "responsible_authority": "...",
  "status": "OPEN"
}
```

## Safety Language
Use:
- discrepancy
- unresolved difference
- missing record
- incomplete public evidence
- requires documentary verification

Avoid unsupported labels such as:
- scam
- fraud
- corruption
- illegal
unless an authoritative source explicitly establishes it.
