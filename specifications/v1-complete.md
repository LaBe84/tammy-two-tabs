# Tammy shared programme intelligence system — v1

**Version:** v1
**Status:** Complete. This is the final v1 phase (Phase 8); there is no Phase 9.

## Implemented in v1

- Notion as the shared programme-state layer (Live Work Register, Source Register, Overlap Map) — see [`shared-programme-intelligence-system.md`](shared-programme-intelligence-system.md).
- Authority-aware source retrieval (Controlled current / Conceptual development / Working draft / External evidence / Archived / Unclassified) — never inferring approval from presence, polish, or repetition.
- Bounded, relevance-driven retrieval (current request → relevant programme state → relevant source metadata → relevant overlap → specific source content only when required) — not whole-database or whole-document-collection dumps.
- Overlap detection across workstreams via the Overlap Map, with UPDATE/LINK/MERGE/KEEP SEPARATE/CREATE NEW disposition — merges proposed only, never executed automatically.
- Structured AI contributions via one common schema and enumeration set, shared by ChatGPT, Tammy-Claude, and Perplexity — see [`contribution-protocol.md`](contribution-protocol.md).
- Human-decision gates on every consequential change (Current Position, Decision Needed, source Authority, Resolved status, merges, new clinical/governance requirements) — `HUMAN DECISION REQUIRED: YES` retained until a human accepts.
- Controlled low-risk write-back — a fixed automatic-write allowlist (provenance only) and blocklist (everything consequential) — see [`write-back-protocol.md`](write-back-protocol.md).
- Stale-state protection — a write aborts with `STATE CHANGED SINCE RETRIEVAL` if the target record changed since it was reasoned about, rather than overwriting it.
- Read-back verification — every write is followed by a read confirming the exact persisted value before success is reported.
- Failure handling — a failed Notion write is reported as `WRITE FAILED`, never claimed as successful; a failed retrieval is reported, never silently backfilled from general knowledge.
- Perplexity evidence ingestion — external evidence enters through the same contribution schema and write-back gates as any other AI source, with no independent write authority — see [`perplexity-ingestion-protocol.md`](perplexity-ingestion-protocol.md).
- Evidence validation — individual source, type, date, jurisdiction, claim/source match, strength, limitations, and whether a stronger original exists, checked before a source is used; weak secondary sources are rejected/downgraded when an original is available.
- Individual source provenance — every material source cited by name, never collapsed into a vague composite ("research literature", "systematic reviews 2017–2026").
- ChatGPT / Tammy-Claude / Perplexity convergence on shared work — three AIs can contribute to the same Live Work Register item or Overlap Key with distinct, attributed contributions, without creating three competing streams of state or three duplicate work items.
- Privacy/data boundary — no automatic propagation of full sensitive content across AI systems; data minimisation preferred; Notion shared memory is not blanket permission to distribute everything to every connected AI.
- The 18 v1 regression invariants (see `shared-programme-intelligence-system.md`, section on regression invariants) — verified across Phases 6, 7, and the Phase 8 final regression below.
- The repository/Notion boundary: Notion owns shared programme state; this repository owns Tammy's own implementation/version history (`versions/version-history.md`, `decisions/decision-log.md` for architecture/technical/implementation decisions, `projects/project-register.md` for repository-level implementation projects).

## Not part of v1

- Any running application, server, UI, or localhost endpoint — Tammy v1 is a governing brief plus a Notion connector, not a deployed service.
- Any OpenAI (or other non-Claude) model integration.
- Full acceptance workflow beyond the low-risk write-back allowlist — there is no mechanism that marks a proposal "accepted" and then automatically promotes it; acceptance is a human act communicated back to Tammy, who then records it as a normal (allowlisted) write.
- Automatic deletion/trashing of Notion pages — no delete/trash tool was available in any phase; test/fixture cleanup requires manual action in Notion.
- Register consolidation beyond what Phase 8 did — `project-register.md`, `decision-log.md`, and `version-history.md` were re-scoped, not deleted or migrated into Notion.
- Any new capability, redesign, or scope expansion beyond Phases 1–8 — none was added in this phase, and none is proposed here.

There is no roadmap beyond this document. Phase 8 is the stop point for v1.
