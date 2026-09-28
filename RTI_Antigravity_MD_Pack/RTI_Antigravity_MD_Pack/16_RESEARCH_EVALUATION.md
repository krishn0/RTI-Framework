# Research Evaluation Plan

## Research Contribution to Demonstrate
The paper should evaluate more than "an LLM can write RTI questions".

Primary system contribution:
**closed-loop evidence intelligence** combining retrieval, structured claims, temporal/relational evidence, contradiction/gap detection, targeted RTI generation and official-response reintegration.

## Experimental Dataset
Prepare 20–50 investigation cases from public records.
For each case manually label:
- relevant documents
- key claims
- source pages
- known contradictions if any
- expected missing records
- expected RTI request categories

## Evaluation Questions
1. Does hybrid retrieval locate the correct evidence?
2. Are generated claims supported by cited sources?
3. Can the system correctly separate different financial concepts?
4. Does contradiction detection avoid false positives caused by temporal revisions?
5. Can the evidence-gap engine identify missing expected records?
6. Does the generated RTI question correspond to the unresolved gap?
7. Does response reintegration resolve previous gaps correctly?

## Metrics
### Retrieval
- Recall@5
- Recall@10
- Mean Reciprocal Rank (optional)

### Evidence
- Citation Accuracy
- Claim Support Rate

### Reasoning
- Contradiction Precision / Recall
- Gap Detection Precision / Recall

### RTI
Human evaluation on:
- relevance
- specificity
- duplicate rate
- traceability to gap

### Closed Loop
- percentage of RTI response facts correctly reintegrated
- percentage of prior gaps correctly updated

## Ablation Ideas
Compare:
- keyword search vs hybrid RAG
- RAG only vs RAG + knowledge relationships
- generic RTI generation vs evidence-gap-driven RTI generation

## Reporting Rule
Do not invent benchmark numbers. Report only measured results.
