# RAG and Vector Database Specification

## Goal
Retrieve the smallest, highest-quality evidence set needed to answer an investigation sub-question.

## MVP Technology
- PostgreSQL
- pgvector
- existing keyword/full-text search
- one embedding model

## Chunking Strategy
### Requirements
- preserve document ID
- preserve document version
- preserve page number
- preserve section/heading where extractable
- never merge text across unrelated pages blindly

### Suggested Chunk Size
Start with roughly 500–900 tokens with modest overlap. Tune only after evaluation.

## Ingestion Flow
```text
Existing Document / Version
 -> extracted page text
 -> clean text
 -> chunk
 -> embed
 -> store document_chunks + vector
```

## Re-Embedding Rules
Re-embed only when:
- a new document version appears
- chunking algorithm version changes
- embedding model version changes

Store processing version metadata to avoid silent inconsistencies.

## Retrieval Flow
```text
sub-question
 -> query normalization
 -> entity/date/department filters
 -> vector retrieval
 -> keyword retrieval
 -> merge candidates
 -> deduplicate
 -> rerank / score
 -> evidence pack
```

## Evidence Pack Schema
```json
{
  "query": "...",
  "filters": {},
  "evidence": [
    {
      "chunk_id": 1,
      "document_id": 10,
      "document_version_id": 3,
      "page_number": 7,
      "text": "...",
      "source_url": "...",
      "semantic_score": 0.0,
      "keyword_score": 0.0,
      "final_score": 0.0
    }
  ]
}
```

## Scoring Guidance
Do not pretend one formula is universally correct. Start with a weighted score from:
- semantic similarity
- keyword match
- entity match
- source type/authority
- date relevance

## Hard Requirements
- no evidence result without provenance
- cap number of chunks sent to LLM
- deduplicate near-identical versions
- favor latest version for current-state questions, but retain earlier versions for temporal analysis
- expose exact document/page source to UI

## Acceptance Tests
1. Query about a known document retrieves the correct page.
2. Query with department filter excludes unrelated departments.
3. A changed document version can retrieve both old/new versions when asking for historical comparison.
4. Duplicate chunks are not returned twice.
5. Retrieval result can be converted to a valid evidence pack without LLM involvement.
