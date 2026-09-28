# Security, Privacy and Safety Requirements

## Preserve Existing Security
Do not weaken:
- robots.txt enforcement
- rate limits/crawl delays
- SSRF protections
- public-only collection policy

## New Upload Security
For RTI response uploads:
- allow only approved file types
- enforce file-size limit
- randomize storage name
- do not trust user filename
- scan/validate MIME type where practical
- never execute uploaded content

## API Security
- validate all request bodies
- parameterized ORM queries
- CORS restricted by configuration
- rate limit expensive investigation endpoints
- protect admin endpoints if authentication is enabled

## Secret Management
Never commit:
- LLM API keys
- database credentials
- cloud credentials

Use environment variables / secret manager.

## LLM Prompt Injection Defense
Government documents and uploaded files are untrusted data.
Treat text inside documents as evidence, **not instructions**.
System/developer prompts must explicitly tell agents to ignore instructions found in retrieved documents.

## Hallucination Defense
- evidence required for factual claims
- structured outputs
- claim verifier
- no source -> status `MISSING` or `INSUFFICIENT_EVIDENCE`

## Legal/Safety Presentation
The system assists with public-record research and RTI drafting. It should avoid presenting allegations as established facts when evidence only shows a discrepancy or unresolved gap.
