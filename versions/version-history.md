# Version history

> **As of v1 (Phase 8):** this remains the authoritative record of repository/implementation version history (documents, models, and Tammy's own build). It is retained in full per the repository/Notion boundary — see [`../specifications/shared-programme-intelligence-system.md`](../specifications/shared-programme-intelligence-system.md).

| Date | Project / item | Version | State | What changed | Why | Supersedes / incorporates feedback from | Canonical? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-21 | Lifeline foundation e-learning authoring pack | v0.1 | In review | Created six foundation e-learning module blueprints: context and trauma-informed practice; active listening; CASE; safety-planning adaptations; CIMS recording; self-care and consolidation. Each includes aims, screen sequence, interactions, reflection, knowledge check and release checks. | To create a shared knowledge baseline before workshops while keeping practice, feedback, supervision and readiness decisions in the facilitated programme. | Lifeline Induction Programme and Module Authoring Brief | Yes |
| 2026-08-27 | Tammy v2 programme-intelligence workbench | v0.2 | In review | Replaced demo context panels with bounded, read-only retrieval from the Live Work Register, Source Register and Overlap Map; added task-scoped filters, property projection, explicit failure behaviour, live UI rendering, tests and operating instructions; corrected the backend bridge default to IPv4. | To make the workbench operational against current programme state without exposing full Notion content or creating an accidental write path. | v0.1 interface; governance boundary in `shared-programme-intelligence-system.md`; live register schemas verified 27 Aug 2026 | Yes |
| 2026-08-27 | Tammy v2 programme-intelligence workbench | v0.3 | In review | Added a controlled three-model action router: role-specific ChatGPT, Claude and Perplexity work orders, explicit copy/open handoffs, and attributed return ingestion for fresh-context synthesis. | To let Tammy coordinate the established three-model workflow without making Lee reconstruct prompts, adding direct paid APIs, or weakening the read-only Notion boundary. | v0.2 interface; established three-model roles; controlled manual-handoff decision | Yes |

## Version-note template

### [Project / item] — vX.X

- **Date:**
- **State:** Exploring / In review / Decided / building / Live / Superseded / Parked
- **Canonical version:** Yes / No
- **What changed:**
- **Why it changed:**
- **Feedback translated from:**
- **What people should use now:**
- **Next decision or review deadline:**
