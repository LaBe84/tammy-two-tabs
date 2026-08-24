# Controlled low-risk write-back protocol (Phase 5)

**Status:** Implemented — low-risk writes only, all other change categories remain proposal-only. See the [implementation sequence](shared-programme-intelligence-system.md#implementation-sequence) in the main specification.

## Core rule

**Writing a contribution to Notion does not make that contribution accepted programme state.** A written record is provenance — it shows a contribution was made and when — not acceptance. Acceptance is a human act, not a write event. Phase 6+ (a formal acceptance mechanism) is not built; until it is, every write under this protocol is either administrative/provenance data or a labelled, unaccepted proposal sitting alongside the existing Current Position, never in place of it.

The Phase 4 structured contribution (see [`contribution-protocol.md`](contribution-protocol.md)) is the mandatory input to every write under this protocol. Nothing is written to Notion that was not first drafted as a structured contribution.

## Automatic write allowlist

Only the following may be written to Notion without a prior explicit human decision in the current interaction:

- `AI Source`
- `Timestamp` / `Last Reviewed`
- a confirmed source URL or reference (`Source Link`, `Source URL`)
- a confirmed document version (`Version`)
- the contribution/proposal record itself (`AI Contribution`, `New Contribution`) — logged as a proposal, not as an update to `Current Position` or `Existing Position`
- an overlap candidate/proposal (a new or updated `Overlap Map` entry left in `Potential overlap` state, never `Merged`)
- a human decision already explicitly given in the current interaction (e.g. the human says "yes, mark that Resolved" — the resulting write is not "automatic", it is the recorded human decision)

## Automatic write blocklist

Tammy must never automatically:

- change `Current Position` / `Existing Position`
- resolve `Decision Needed`
- change `Authority` (source or work item)
- mark consequential work `Resolved` / complete
- merge work items (`Merge State` → `Merged`, or `Human Decision` → `Accept merge`)
- reopen resolved work
- create a new clinical requirement
- create a new governance requirement
- replace a recorded human decision
- convert AI inference into evidence
- convert external evidence into local policy
- approve developmental or working-draft material (change its `Authority` toward `Controlled current`)

Any contribution that would require one of these stays a **proposal**: recorded in the response (and, where useful, as a provenance write per the allowlist — e.g. logging the proposal text itself), never executed against the blocked field, with `HUMAN DECISION REQUIRED: YES`.

## Write classification

Every candidate write is classified before anything is sent to Notion:

- **LOW-RISK WRITE** — touches only allowlisted fields. Proceeds through the write safety sequence below.
- **CONSEQUENTIAL PROPOSAL** — touches a blocklisted field, or a human decision has not yet been given in this interaction. Never written to the blocked field. Presented as a Phase 4 contribution with `HUMAN DECISION REQUIRED: YES`.
- **PROHIBITED AUTOMATIC WRITE** — a CONSEQUENTIAL PROPOSAL that something in the interaction is pushing to be written anyway (e.g. an instruction to "just update it"). Refused outright, not merely deferred; the refusal and the reason are stated.

## Write safety sequence

Before every write classified LOW-RISK:

1. Retrieve the target record again from Notion (fresh read, not a cached one from earlier in the reasoning).
2. Confirm its current state has not materially changed since the state the contribution was reasoned against. If it has, stop — see Concurrency rule.
3. Identify exactly which fields will change.
4. Classify the write (LOW-RISK / CONSEQUENTIAL PROPOSAL / PROHIBITED AUTOMATIC WRITE, above).
5. Preserve existing programme state — the write payload includes only the fields being changed; nothing else is touched or overwritten.
6. Write only the permitted fields.
7. Read the record back after writing.
8. Verify the persisted value matches the intended value, field by field.
9. If verification fails, report `WRITE FAILED` — do not report success.
10. Never report success without successful read-back verification.

## Duplication check

Before creating any new contribution or candidate item in Notion:

1. Search the Live Work Register for a matching or related work item.
2. Search the Overlap Map for a matching `Overlap Key`.
3. Compare the underlying issue, not just the wording.
4. Check whether a materially equivalent contribution already exists (same issue, same or subsumed claim).

If a duplicate exists: do not create another record. Classify the new input as `CLASSIFICATION: NO MATERIAL CHANGE`, `RECOMMENDED DISPOSITION: NO CHANGE`, and say so rather than silently doing nothing.

## Concurrency rule

If the target Notion record has materially changed between the retrieval that grounded the reasoning and the moment of writing:

**Stop the write.** Return `STATE CHANGED SINCE RETRIEVAL` and prepare a refreshed proposal against the new state. Never overwrite the newer state, even if the newer state looks like it came from a lower-authority source — a stale write can silently erase a legitimate concurrent update.

## Failure rule

If a Notion write fails:

- Do not retry destructively (no blind retries that could double-write or corrupt state).
- Do not claim success.
- Preserve the proposed contribution locally, in the response — it is not lost, only not yet persisted.
- Report the exact failure (error code/message where available).
- Leave accepted programme state unchanged — a failed write must never leave the record in a partially-updated, undocumented state.

## What this phase does not do

- No acceptance workflow. A written provenance/contribution record is not "accepted" by anyone reading this protocol — that mechanism does not exist yet (Phase 6+).
- No automatic resolution of anything in the blocklist, regardless of how confident the contribution's `CONFIDENCE` field is.
- No retry-with-backoff or queuing on failure — a failed write is reported and left for the next attempt to pick up fresh.
