# Perplexity ingestion protocol (Phase 7)

**Status:** Implemented. Perplexity contributions use the existing Phase 4 contribution schema and the existing Phase 5 write-back controls — there is no separate Perplexity state model, no separate write path, and no separate authority system.

## Perplexity's role

Perplexity is an **external evidence engine** (see [`shared-programme-intelligence-system.md`](shared-programme-intelligence-system.md), section S/T/U). Its output:

- May `SUPPORT EXISTING`, `CHALLENGE EXISTING`, `EXTEND EXISTING`, or identify a genuinely `NEW ISSUE`.
- Does **not** establish current Lifeline policy, implementation, approval, ownership, governance requirements, or local clinical requirements — regardless of how strongly a source states a recommendation.

Every Perplexity contribution is drafted using the same schema as a ChatGPT or Tammy-Claude contribution (`AI SOURCE` = `Perplexity`), per [`contribution-protocol.md`](contribution-protocol.md). No new fields, no new enumerations, no separate register.

## Evidence validation gate

Before a Perplexity contribution is promoted beyond raw research into a structured contribution, validate:

1. The individual original source (not a secondary aggregator, unless no original exists).
2. Source type (systematic review, primary study, guideline, commentary, aggregator...).
3. Publication date.
4. Jurisdiction.
5. Claim/source match — does the source actually say what the contribution claims it says?
6. Evidence strength (Strong / Moderate / Weak / Unknown).
7. Limitations.
8. Whether a stronger or more original source exists for the same claim.
9. Whether the evidence conflicts with existing programme evidence or position.
10. Whether the finding is genuinely new, or restates something already recorded.

**Where a secondary aggregator restates a claim that a stronger original source also supports, the aggregator is rejected or downgraded** (`AI Use: Do not use unless requested`, or an equivalent authority note explaining why) — it is not treated as equivalent evidence. The rejection itself is recorded in the Source Register with a note explaining what it was rejected in favour of, so the decision has provenance too.

## Individual source provenance

Every material external source is registered and cited individually. Contributions must never collapse multiple distinct sources into a vague composite ("research literature", "systematic reviews 2017–2026") where the individual sources are material to the claim. Each source gets its own Source Register entry with its own `Authority`, `AI Use`, and `Authority Note`.

## Deduplication before contribution

Before creating any new programme contribution from Perplexity output:

1. Search the Live Work Register for a matching or related work item.
2. Search the Source Register for an already-registered source covering the same claim.
3. Search the Overlap Map for a matching `Overlap Key`.
4. Search existing material contributions already logged against that item/overlap.

Classify: `SUPPORTS EXISTING` / `CHALLENGES EXISTING` / `EXTENDS EXISTING` / `NEW ISSUE` / `NO MATERIAL CHANGE`. **Multiple external sources supporting one underlying issue must not automatically create multiple programme work items** — they are logged as multiple, individually-provenanced pieces of evidence against the *same* work item or overlap key.

## No direct raw-research promotion

Raw Perplexity output never directly alters accepted programme state. The required flow is:

```
PERPLEXITY RESEARCH
  → VALIDATION (evidence validation gate, above)
  → STRUCTURED CONTRIBUTION (Phase 4 schema, AI SOURCE: Perplexity)
  → DEDUPLICATION / OVERLAP CHECK
  → PROPOSED DISPOSITION
  → HUMAN DECISION WHERE CONSEQUUENTIAL (HUMAN DECISION REQUIRED: YES)
  → ONLY THEN: permitted persistence, under the existing Phase 5 write-back rules
```

Phase 5's rules apply to Perplexity contributions exactly as they apply to Tammy's or ChatGPT's: the automatic-write allowlist/blocklist, the write safety sequence (re-retrieve, classify, write only permitted fields, read back, verify), the duplication check, the concurrency check, and the failure rule (see [`write-back-protocol.md`](write-back-protocol.md)) all apply unchanged. **Phase 7 grants Perplexity no independent write authority** — a Perplexity-sourced write is subject to exactly the same gates as any other write, and is made by Tammy following those gates, not by Perplexity directly.

## Three-AI convergence

When ChatGPT, Tammy-Claude, and Perplexity each contribute to the same underlying issue:

- All three map to the **same** Live Work Register item and/or Overlap Map `Overlap Key` — found via the deduplication step above, not assumed.
- Each contribution's `AI Source` is recorded distinctly (the Live Work Register's `AI Source` and the Overlap Map's `Sources` fields are multi-select for exactly this reason) — provenance is never merged into a single unattributed blob.
- Evidence (what a source says) and inference (what an AI concludes from it) stay labelled as what they are.
- No duplicate work item or duplicate overlap entry is created for the same underlying issue.
- If the three disagree, the disagreement is preserved (per the contradiction-handling procedure in the main specification), not averaged into a single synthesised position.
- The `Overlap Key` (or Live Work Register item) that already exists stays the anchor — the point of the exercise is that the AIs contribute to the **same** programme intelligence, not that they each produce their own.
- Accepted `Existing Position`/`Current Position` is not changed by the act of three AIs agreeing — agreement is not the same as human acceptance. Anything consequential still carries `HUMAN DECISION REQUIRED: YES`.
