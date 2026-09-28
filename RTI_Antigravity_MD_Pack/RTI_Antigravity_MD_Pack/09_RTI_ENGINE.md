# RTI Generation Engine

## Goal
Generate precise, record-oriented RTI requests only for information that remains unresolved after public-evidence search.

## Inputs
- investigation ID
- evidence gaps
- project/entity context
- already-known public information
- candidate public authority

## Pipeline
```text
Gap
 -> check whether record is already publicly available
 -> normalize requested record
 -> resolve likely authority
 -> create specific question
 -> remove duplicates
 -> group related questions
 -> produce draft
```

## Question Design Rules
Prefer requests for records, copies, dates, orders, statements, registers and reports.
Avoid vague questions asking officials to create explanations not contained in records.

Good:
- "Please provide a certified copy of the order approving extension of the completion deadline for Project X."

Weak:
- "Why did the project get delayed?"

Better conversion:
- "Please provide copies of records, file notings, correspondence and approvals recording reasons for extension of the completion deadline for Project X."

## RTI Draft Data Model
```json
{
  "authority": "...",
  "subject": "Information regarding Project X",
  "context": "...",
  "questions": [
    {
      "sequence": 1,
      "gap_id": 10,
      "requested_record_type": "extension_order",
      "question_text": "..."
    }
  ]
}
```

## Deduplication
Questions should be merged when they request the same record for the same time range.

## Human Review
Generated RTI must be editable before submission/export.
Do not automatically submit legal requests without explicit user action.

## MVP Outputs
- JSON draft
- formatted text preview
- printable/exportable frontend representation
