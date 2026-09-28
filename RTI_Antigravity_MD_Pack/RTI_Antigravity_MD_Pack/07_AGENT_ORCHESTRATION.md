# Multi-Agent Orchestration Specification

## Core Principle
Agents are specialized services with strict inputs/outputs, not independent chatbots.

## Required Agents for MVP
1. Investigation Planner
2. Government Data Agent
3. Tender + Budget Agent
4. Audit + Timeline Agent
5. Knowledge / Evidence Agent
6. Evidence Verifier (deterministic service where possible)
7. RTI Agent

## Investigation Planner
Input:
```json
{
  "investigation_id": 1,
  "user_query": "...",
  "known_entities": []
}
```

Output:
```json
{
  "intent": "project_investigation",
  "entities": [],
  "sub_questions": [
    {
      "id": "Q1",
      "question": "...",
      "required_agents": ["government_data"],
      "required_evidence_types": ["government_document"]
    }
  ]
}
```

## Shared Agent Input
```json
{
  "investigation_id": 1,
  "sub_question": "...",
  "evidence_pack": {},
  "entity_context": {}
}
```

## Shared Agent Output
```json
{
  "agent": "tender_budget",
  "findings": [
    {
      "subject": "Project X",
      "predicate": "contract_value",
      "value": "...",
      "source_refs": ["chunk:123"],
      "status": "PROPOSED"
    }
  ],
  "missing_information": [],
  "notes": []
}
```

## Router Rules
- invoke only relevant agents
- parallelize independent agents if infrastructure supports it
- cap total agent calls per investigation
- prevent recursive uncontrolled agent spawning
- preserve all inputs/outputs in `investigation_steps`

## Government Data Agent
Extract:
- project identity
- department
- scheme
- official dates
- public orders/circulars
- current status if explicitly supported

## Tender + Budget Agent
Extract separately:
- sanctioned amount
- tender estimate
- awarded value
- contractor
- fund release
- expenditure

Never treat these values as equivalent.

## Audit + Timeline Agent
Extract:
- audit observations
- deadlines
- revised deadlines
- extension orders
- work orders
- major public events

## Knowledge / Evidence Agent
- resolve relationships
- find corroborating documents
- attach source refs
- build/update entity context

## Agent Failure Policy
If one agent fails:
- mark its step failed
- keep other results
- expose partial completion
- do not fabricate missing results

## LLM Output Validation
Every LLM-generated object must be parsed into a Pydantic schema. Invalid output must not reach the database.
