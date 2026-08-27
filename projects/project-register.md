# Project register

> **As of v1 (Phase 8):** this file tracks **repository/implementation projects only** — work on Tammy herself. It is not a second Live Work Register. Current shared Lifeline programme state (CARE, CRG, Induction, ERO, SAI, PORF-CASE, SMHS — including the Lifeline foundation e-learning build) lives in Notion's **Tammy — Live Work Register**, governed by [`../specifications/shared-programme-intelligence-system.md`](../specifications/shared-programme-intelligence-system.md). Query Notion for current programme status; do not maintain a parallel copy here.

| Project | State | Outcome | Canonical version | Review window | Owner | Next move | Risks / dependencies |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tammy shared programme-intelligence system | Live | v1: read-only Notion retrieval, structured AI contributions, controlled low-risk write-back, Perplexity ingestion, full regression suite | v1 (Phases 1–8) | N/A — implementation complete, reviewed on request | Tammy Two Tabs | Maintain; no further phases planned | Notion connector availability; workspace query limits |
| Tammy v2 programme-intelligence workbench | In review | Local three-column interface with live Tammy reasoning and bounded, read-only Notion retrieval in the right context rail | v0.2 on `feature/tammy-v2-interface` | Real-register acceptance test on Lee's Mac | Lee / Tammy Two Tabs | Pull the branch, start the bridge with the existing Notion token, then verify one CARE/Induction query end to end | Token must be available to the bridge process; the Notion integration must have read access to all three controlled registers; no write route is included |

## Triage for a new request

- **Fold in:** advances an existing project without changing its scope.
- **New project:** has a distinct outcome, audience, or deadline.
- **Park:** worthwhile but not a current commitment.
- **Delegate:** bounded research, drafting, critique, checking, or implementation work suitable for a specialist agent.
