# Structured contribution protocol (Phase 4)

**Status:** Implemented — proposal only. No write-back. See the [implementation sequence](shared-programme-intelligence-system.md#implementation-sequence) in the main specification.

This is Tammy's implementation of the specification's common cross-AI contribution protocol (section J). It converts a material interaction into a structured, typed proposal that is explicitly distinguishable from accepted Notion programme state. Producing a contribution never writes to Notion, changes Current Position, resolves Decision Needed, merges work items, changes source authority, or marks work complete — those all remain Phase 5+ and out of scope here.

## When to produce a contribution

Per section Z of the main specification, after substantive work ask whether the interaction produced: new evidence, a new finding, an accepted decision, a new action, a status change, a contradiction, an overlap, a resolution, or a supersession. If yes, produce a contribution using the schema below. If no, do not.

## Schema

```
AI SOURCE:
WORKSTREAM:
WORK ITEM:
CONTRIBUTION TYPE:
EXISTING POSITION:
CONTRIBUTION:
EVIDENCE/SOURCE:
SOURCE AUTHORITY:
EVIDENCE STRENGTH:
WHAT IS GENUINELY NEW:
OVERLAP KEY:
CLASSIFICATION:
RECOMMENDED DISPOSITION:
CONFIDENCE:
HUMAN DECISION REQUIRED:
TIMESTAMP:
```

### Field notes

- **AI SOURCE** — `ChatGPT` / `Tammy-Claude` / `Perplexity`, matching the Live Work Register's `AI Source` options.
- **WORKSTREAM** — matches a Live Work Register `Workstream` value (Lifeline, CARE, CRG, Induction, ERO, SAI, PORF-CASE, SMHS, Other) where applicable.
- **WORK ITEM** — the Live Work Register item this contribution relates to, retrieved read-only before drafting the contribution (per Phases 1–3). If no existing item matches, say so explicitly rather than inventing one.
- **EXISTING POSITION** — the Live Work Register's `Current Position` (or Overlap Map's `Existing Position`) at retrieval time, quoted or closely paraphrased. This is what the contribution is being compared against — never silently overwritten by drafting a contribution.
- **CONTRIBUTION** — the new material itself, stated plainly.
- **EVIDENCE/SOURCE** — what grounds the contribution: a Source Register entry, a Live Work Register record, an Overlap Map entry, or an explicit statement that no register entry exists.
- **SOURCE AUTHORITY** — one of the six authority states (Controlled current / Conceptual development / Working draft / External evidence / Archived / Unclassified), taken from the Source Register where the source is registered, or `Unclassified` where it is not.
- **EVIDENCE STRENGTH** — Strong / Moderate / Weak / Unknown, matching the Live Work Register's scale.

### Valid enumerations

**CONTRIBUTION TYPE** — one of: `NEW FINDING`, `NEW EVIDENCE`, `CHALLENGE`, `DECISION SUPPORT`, `NEW ACTION`, `STATUS CHANGE`, `CONTRADICTION`, `OVERLAP`, `RESOLUTION CANDIDATE`.

**CLASSIFICATION** — one of: `SUPPORTS EXISTING`, `CHALLENGES EXISTING`, `EXTENDS EXISTING`, `NEW ISSUE`, `NO MATERIAL CHANGE`.

**RECOMMENDED DISPOSITION** — one of: `UPDATE EXISTING`, `LINK`, `MERGE`, `KEEP SEPARATE`, `CREATE NEW`, `NO CHANGE`.

- `MERGE` is a recommendation only. Per the specification's overlap states and human-authority rules, a contribution can never execute a merge — it can only propose one, with `HUMAN DECISION REQUIRED: YES`.

**HUMAN DECISION REQUIRED** — `YES` or `NO`. `YES` whenever the contribution would, if accepted, change Current Position, resolve a Decision Needed, merge or relate work items, change source authority, change clinical or governance direction, reopen resolved work, or create a new programme requirement — i.e. any of the consequential-change categories in section R of the main specification. Low-risk administrative detail (a timestamp, a source link, a confirmed version number) may be `NO`.

## Producing a contribution: procedure

1. Identify the material interaction and what changed (per section Z).
2. Retrieve the relevant Live Work Register record(s), Source Register entries, and Overlap Map entries — read-only, as in Phases 1–3. Do not skip retrieval and assume no existing record.
3. Compare the new material against `EXISTING POSITION`. Do not average a disagreement into a blended position — if they conflict, that is a `CONTRADICTION`, not a `CHALLENGES EXISTING` restated as fact.
4. Classify (`CLASSIFICATION`) and recommend a disposition (`RECOMMENDED DISPOSITION`) from the fixed enumerations. Semantic similarity alone never justifies `MERGE`.
5. Set `HUMAN DECISION REQUIRED` per the consequential-change rule above.
6. Present the completed schema as a proposal. Label it clearly as a proposal — for example, a heading such as "Proposed contribution (not yet accepted)" — so it cannot be mistaken for a Live Work Register record. Nothing is written to Notion.
7. The human accepts, amends, or rejects the proposal. Only human acceptance (Phase 5+, not yet implemented) would ever move information into Notion.

## Distinguishing a contribution from accepted state

A contribution is data about a possible change, not the change itself. Concretely, in this repository:

- A contribution is a block of text following the schema above, presented in a reply or a scratch file — never appended into `projects/project-register.md`, `decisions/decision-log.md`, or `versions/version-history.md` as if it were settled fact.
- A contribution never edits an existing Live Work Register `Current Position`, Overlap Map `Existing Position`, or Source Register `Authority` value, because Phase 4 has no write access and no Phase 5 write-back exists yet.
- Where a contribution is later accepted by a human and something needs recording in the repository (e.g. a Tammy implementation decision), that recording happens explicitly in `decisions/decision-log.md` as a normal decision entry — distinct from, and citing, the contribution that prompted it.
