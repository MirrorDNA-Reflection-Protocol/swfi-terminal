# SWFI AI Governance Spec v0.1

Generated for SWFI Beta - Capital Intelligence Layer v0.1

## Purpose

SWFI AI exists to extract, compare, rank, and explain sovereign and institutional investor intelligence from approved sources. It does not invent facts, smooth over conflicts, or publish unsupported conclusions.

## Product Promise

- Evidence-bound intelligence
- Stable outputs
- Controlled interpretation
- Traceable provenance
- Institutional tone

## Core Objects

Freeze these labels and do not allow model-created categories:

- `Profile`
- `Fund`
- `KeyPerson`
- `Transaction`
- `Mandate`
- `RFP`
- `AssetAllocation`
- `Document`
- `Source`
- `Evidence`
- `Nugget`
- `Confidence`
- `Status`

## Status Model

- `Verified`: directly supported by a high-authority source or confirmed across multiple approved sources
- `Derived`: reasonable interpretation from verified facts, clearly labeled as interpretation
- `Conflicted`: approved sources disagree
- `Missing`: required field not yet supported
- `NeedsReview`: high-value or high-risk claim awaiting analyst review
- `Rejected`: model output failed evidence or policy checks

## Confidence Model

Use rule-based confidence, not freeform model judgment.

- `High`: primary source or two strong sources agree
- `Medium`: one strong source or multiple weaker sources align
- `Low`: partial support, stale support, or indirect evidence
- `None`: no reliable support

## Approved Source Classes

- `Primary`: official institution websites, filings, board minutes, annual reports, procurement notices, official speeches, exchange announcements
- `Secondary`: reputable news, wire services, association sites, conference sites, consultant documents
- `PlatformInternal`: SWFI canonical records, change logs, prior reviewed nuggets
- `ExternalStructured`: approved APIs such as SWFI API, SEC, GLEIF, Companies House, OFAC
- `Unapproved`: social content, unlicensed scraped data, unverifiable blog posts

## Source Priority

When sources conflict, prefer:

1. Primary current document
2. Primary current website
3. External structured authoritative registry
4. Secondary high-reputation coverage
5. Historical SWFI record
6. Unapproved source is never decisive

## Required Evidence Bundle

Every important output must carry:

- `source_system`
- `source_type`
- `source_url_or_doc_id`
- `retrieved_at`
- `published_at` if available
- `evidence_excerpt`
- `field_path_or_location`
- `extraction_method`
- `model_version`
- `prompt_version`
- `policy_version`

## Output Contract

Use structured output only. Client-facing prose must be rendered from validated structured records.

Required top-level fields:

- `schema_version`
- `entity_id`
- `entity_type`
- `claim`
- `observed_fact`
- `derived_implication`
- `status`
- `confidence`
- `commercial_relevance`
- `novelty_score`
- `recency_score`
- `evidence_strength`
- `source_refs`
- `contradictions`
- `review_required`
- `why_it_matters`

## Hard Rules

- No claim without at least one attached source reference
- No `Verified` status from a single weak source
- No prediction stated as fact
- No silent resolution of conflicting numbers
- No client-facing output from raw model prose
- No published nugget without schema-valid JSON
- No broad web generation in client answers unless explicitly labeled `External`

## Fact vs Interpretation

Always separate:

- `Observed fact`
- `Derived implication`

Example:

- Observed fact: board agenda includes private credit allocation review
- Derived implication: potential near-term mandate activity in private credit

Never merge these into one confident sentence.

## Refusal Policy

The model must refuse when support is insufficient. Approved phrases:

- `Not verified from current SWFI sources`
- `Conflicting source evidence`
- `Insufficient support for a reliable conclusion`
- `Requires analyst review`

## Model Role Split

Use models as components, not as truth engines.

- `Anthropic`: long-document reading, nuanced extraction, contradiction review, synthesis from large source packets
- `OpenAI`: structured extraction, normalization, classification, dedupe, ranking, short-form controlled drafting

Neither model may publish directly to UI without schema validation and policy checks.

## Pipeline

1. Ingest approved records and documents
2. Detect changes against prior canonical state
3. Extract candidate facts from changed material
4. Build evidence bundle
5. Generate structured candidate nuggets
6. Apply deterministic policy checks
7. Score novelty, relevance, recency, and evidence strength
8. Route high-risk items to review
9. Publish only approved fields and statuses
10. Log everything for replay

## Scoring

Use fixed weights.

- `commercial_relevance`: 35%
- `evidence_strength`: 25%
- `recency`: 20%
- `novelty`: 10%
- `source_authority`: 10%

Do not let the model invent the weighting.

## Human Review Gates

Always require review for:

- contact inference
- mandate prediction
- politically sensitive claims
- benchmark comparisons
- contradictory AUM or allocation figures
- homepage research claims
- report downloads sent to clients

## Anti-Drift Controls

- Pin `schema_version`
- Pin `prompt_version`
- Pin `policy_version`
- Track model id used on each output
- Keep a gold evaluation set
- Block promotion if benchmark quality degrades

## Gold Evaluation Set

Maintain a fixed pack:

- 50 profile truth cases
- 50 key people change cases
- 50 transactions
- 25 mandate or RFP cases
- 25 conflict cases
- 25 refusal cases

Metrics:

- schema compliance
- unsupported claim rate
- contradiction miss rate
- refusal accuracy
- reviewer override rate
- nugget usefulness score

## UI Rules

Display only these trust states:

- `Verified`
- `Derived`
- `Conflicted`
- `Missing`
- `Needs Review`

Every displayed nugget should expose:

- status
- confidence
- source
- updated time
- evidence drawer

## Publishing Gates

A nugget can publish only if:

- schema valid
- at least one source attached
- no unresolved policy violation
- confidence and status assigned deterministically
- review complete if required

## Operational Principle

SWFI AI does not invent. It extracts, compares, scores, and explains. The system should prefer a narrow refusal over a broad but unsupported answer.
