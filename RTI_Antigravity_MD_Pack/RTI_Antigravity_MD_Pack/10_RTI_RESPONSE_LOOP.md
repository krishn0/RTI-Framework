# RTI Response Intelligence and Closed Loop

## Goal
Turn an official response into new structured evidence and update the original investigation.

## Input
- RTI application
- ordered RTI questions
- uploaded official response PDF/text

## Processing Flow
```text
upload
 -> reuse existing document extraction/OCR
 -> segment response
 -> align response sections to original questions
 -> classify completeness
 -> extract new claims/attachments/references
 -> verify and store new evidence
 -> update gaps
 -> update knowledge relationships
 -> re-run affected investigation steps
```

## Classification Labels
- `ANSWERED`
- `PARTIAL`
- `NOT_ANSWERED`
- `DOCUMENT_ATTACHED`
- `TRANSFERRED`
- `EXEMPTION_CITED`
- `UNCLEAR`

## Important Rule
The system may classify completeness based on whether requested records/information appear to have been supplied, but it must not present legal conclusions about validity of an exemption or legal compliance unless separately reviewed.

## Reintegration
New claims extracted from an official response must carry provenance:
- RTI response ID
- page
- exact excerpt
- received date if known

## Re-Investigation Trigger
Only rerun investigation components affected by newly supplied evidence.
Example:
- new payment statement -> rerun money trail + gap detector
- new extension order -> rerun timeline + contradiction resolver

## Closed-Loop Success Condition
A prior gap can transition:
```text
MISSING -> PARTIAL -> SUPPORTED / VERIFIED
```

The history of state transitions must remain auditable.
