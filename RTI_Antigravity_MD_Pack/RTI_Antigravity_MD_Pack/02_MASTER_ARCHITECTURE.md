# Master Architecture

## High-Level Flow

```text
User Query
  |
  v
Query Understanding
  |
  v
Hybrid Evidence Retrieval
  |---- PostgreSQL metadata
  |---- pgvector semantic retrieval
  |---- keyword search
  `---- knowledge-graph traversal
  |
  v
Investigation Planner
  |
  v
Agent Router
  |---- Government Data Agent
  |---- Tender + Budget Agent
  |---- Audit + Timeline Agent
  `---- Knowledge/Evidence Agent
  |
  v
Evidence Reasoning Layer
  |---- claim normalization
  |---- cross-source verification
  |---- contradiction detection
  |---- temporal reasoning
  |---- money-trail reasoning
  `---- evidence-gap detection
  |
  +--> Known / Supported Findings --> Evidence Report
  |
  `--> Missing / Unresolved Facts --> RTI Engine
                                      |
                                      v
                                RTI Application
                                      |
                                      v
                               Official Response
                                      |
                                      v
                            Response Intelligence
                                      |
                                      v
                              Knowledge Update
                                      |
                                      `----> Re-investigation
```

## Logical Layers

### Layer A — Existing Public Information Layer
Uses current CoreScapper data.

### Layer B — Evidence Memory
- relational records: PostgreSQL
- semantic memory: pgvector
- graph relationships: PostgreSQL first, Neo4j optional later

### Layer C — Investigation Intelligence
- query parser
- planner
- router
- agents

### Layer D — Accountability Reasoning
- evidence verification
- contradiction detection
- expected evidence model
- gap detection
- timeline/money-trail reasoning

### Layer E — RTI Loop
- authority resolution
- record-oriented question generation
- official-response parsing
- question-response matching
- graph/evidence update

### Layer F — User Experience
- investigation screen
- evidence report
- known vs missing
- timeline
- money trail
- contradictions
- RTI draft
- RTI response analysis
- project digital twin

## Architectural Decision: PostgreSQL First
For the MVP:
- PostgreSQL remains the system of record.
- `pgvector` stores embeddings.
- graph relationships are represented in normalized relational tables.
- Neo4j is optional after the MVP.

This reduces operational complexity while preserving upgrade paths.
