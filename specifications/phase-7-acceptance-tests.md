# Phase 7 acceptance tests — Perplexity ingestion and three-AI convergence

Run 2026-08-24. No real, completed Perplexity research run exists yet in this workspace's Source Register (it held 4 entries, none tagged `External research`, before this run). Rather than fabricate citations that could be mistaken for real published research, this run uses a **clearly labelled synthetic test fixture** — the same non-clinical, clearly-identified-test-data principle used for the Phase 5/6 TEST record — to exercise the ingestion mechanism against real, live Notion data.

**Fixture (synthetic, not real research):**
- **Source A** — original, primary-source-type, Strong evidence, supports the existing calibration framing. Registered: https://app.notion.com/3c6174d2d1ac81fc8783d53d9f55cc50 (Authority: External evidence, AI Use: Evidence not local policy).
- **Source B** — weak secondary aggregator restating Source A with no primary data. Registered but rejected/downgraded: https://app.notion.com/3c6174d2d1ac815aa0eac5254413829e (Authority: Unclassified, AI Use: Do not use unless requested).
- **Source C** — original, Moderate evidence, argues calibration is primarily a training problem rather than a documentation/artefact problem — partially in tension with the existing framing. Registered: https://app.notion.com/3c6174d2d1ac81ea8df9daadbfe51443 (Authority: External evidence, AI Use: Evidence not local policy).

**Anchor (real, existing, unchanged in identity):** Overlap Map entry `assessment-formulation-consistency`, https://app.notion.com/3c6174d2d1ac81189662cbec5450941e — Existing Position, State (`Potential overlap`), and Human Decision (`Pending`) were the same before and after this run.

---

## Test A — fixture ingestion

**Action:** Retrieved the existing `assessment-formulation-consistency` Overlap Map entry, ran the evidence validation gate over Sources A, B, C, and appended a validated Perplexity contribution to `New Contribution` (allowlisted field) via `update_page`.

**Validation gate applied:** A = original, Strong, claim/source match confirmed by fixture design → validated, `CLASSIFICATION: SUPPORTS EXISTING`. B = secondary aggregator of A with no independent data, and a stronger original (A) exists → rejected/downgraded. C = original, Moderate, claim/source match confirmed → validated, `CLASSIFICATION: CHALLENGES EXISTING` (partial).

**Read-back:** re-fetched the page; `New Contribution` contains the new Perplexity-attributed text exactly as written; `Existing Position`, `State`, `Human Decision` unchanged.

**PASS check:** correctly validated and mapped to the existing overlap. **PASS.**

---

## Test B — weak source

**Action:** Source B (weak secondary aggregator) was evaluated against the validation gate's question 8 ("does a stronger/original source exist for the same claim?"). Source A is that stronger original.

**Result:** Source B was **not** used to support the material claim. It is registered in the Source Register (for provenance of the rejection itself) with `Authority: Unclassified` and `AI Use: Do not use unless requested`, and its `Authority Note` states explicitly that it was rejected/downgraded in favour of Source A. No contribution text treats Source B's claim as evidence.

**PASS check:** rejected/downgraded pending original-source verification — and the original (Source A) was in fact available and used instead. **PASS.**

---

## Test C — provenance

**Action:** Reviewed the Source Register after fixture ingestion.

**Result:** Sources A, B, and C each have their own Source Register page with their own `Authority`, `AI Use`, and `Authority Note` — none were collapsed into a composite entry like "external research" or "systematic reviews". The Overlap Map's `New Contribution` text also names each source individually ("SYNTHETIC Source A...", "SYNTHETIC Source C...", "SYNTHETIC Source B... REJECTED") rather than referring to "the evidence" generically.

**PASS check:** individual provenance retained for each material source. **PASS.**

---

## Test D — deduplication

**Action:** Three external sources (A, B, C) all address the same underlying issue (`assessment-formulation-consistency`). Before writing anything, searched the Live Work Register and Overlap Map for that issue — found it already existed as one Overlap Map entry with three related Live Work Register items (CARE Log, Induction, PORF/CASE).

**Result:** All three sources' findings were logged as one appended note on the **existing** Overlap Map entry. No new Live Work Register item and no new Overlap Map entry was created. Live Work Register item count before and after this run: 8 (unchanged) — confirmed by re-querying the full register.

**PASS check:** no three new programme work items were created for three external sources addressing one issue. **PASS.**

---

## Test E — three-AI convergence

**Action:** In the same write, logged three distinct contributions against the same Overlap Map entry:

- **Perplexity** (synthetic fixture): validated Sources A and C, `SUPPORTS EXISTING` / `CHALLENGES EXISTING`.
- **Tammy-Claude**: the existing calibration/overlap analysis already on record (from Phase 4), reused rather than duplicated.
- **ChatGPT** (synthetic fixture, for this test only): a reasoning/design finding — calibration as "a shared reasoning contract" of required judgement moves that CARE/induction/PORF-CASE each instantiate differently — `EXTENDS EXISTING`.

`Sources` (the Overlap Map's provenance field) was updated from `["ChatGPT","Human"]` to `["ChatGPT","Tammy-Claude","Perplexity","Human"]` — each AI's involvement is recorded, not merged into an anonymous "AI" label. The three contributions remain individually attributed within `New Contribution`'s text (each paragraph is prefixed with its source and date).

**Result:** One Overlap Map entry (`OVL-1`, `assessment-formulation-consistency`), one `Overlap Key`, no duplicate. Existing Position untouched. Human Decision still `Pending`. Source C's training-centred framing is recorded as in partial tension with the existing artefact-centred framing rather than silently merged into agreement — the disagreement is visible in the text, not erased.

**PASS check:** all three contributions map to the existing underlying work; provenance identifies which AI produced each; no duplicate work item; disagreement preserved; overlap key unchanged; Current Position not silently changed. **PASS.**

---

## Test F — contradiction

**Action:** Source C's claim ("calibration is primarily addressed through training and deliberate practice, not documentation/artefact redesign") is in tension with the existing Overlap Map framing, which treats the problem partly as a shared-specification/documentation-architecture question (`Proposed Merge`: "create one common reasoning/calibration specification").

**Recorded (in the `New Contribution` write):**

```
EXISTING POSITION: CARE, secondary assessment and induction rely on counsellors recognising change, uncertainty, drivers, foreseeable deterioration and proportionate response; the proposed route to consistency (per Proposed Merge) is a shared specification/documentation approach.
EXTERNAL EVIDENCE: SYNTHETIC Source C — calibration is primarily a training/deliberate-practice problem.
SOURCE/AUTHORITY: External evidence (Source Register), Moderate strength, original.
NATURE OF CONTRADICTION: differing emphasis on where the fix belongs — documentation/specification design vs. training/practice design. Not a direct factual conflict, but a genuine tension in disposition.
WHAT WOULD RESOLVE IT: evidence on which lever (specification design vs. training design) produces measurably more consistent counsellor reasoning; or a human decision that both are needed and in what sequence.
CURRENT SAFE CONCLUSION: neither route is adopted; the tension is logged against the existing Overlap Map entry, not resolved.
HUMAN DECISION REQUIRED: YES
```

**Verification:** the Overlap Map's `Existing Position` was not edited to adopt either framing; `Human Decision` remains `Pending`.

**PASS check:** contradiction preserved; local position not automatically replaced. **PASS.**

---

## Test G — local authority

**Action:** Source A and Source C both state their claims strongly (per fixture design — Source A: "structured calibration tools improve inter-rater consistency"; Source C: "training and deliberate practice" as the primary lever).

**Result:** Both are registered with `Authority: External evidence` and `AI Use: Evidence not local policy` in the Source Register. Neither claim was written anywhere as Lifeline policy, an approved practice, or an operational requirement — they are recorded as evidence informing an already-`Pending` human decision on an already-`Potential overlap` item.

**PASS check:** strongly-stated external recommendations are not represented as current Lifeline policy. **PASS.**

---

## Test H — human authority

**Action:** Drafted (not written to Notion beyond the logged evidence) the consequential disposition implied by this evidence — e.g. "adopt a structured calibration tool as a CARE requirement" or "make deliberate-practice training the primary induction mechanism for calibration."

```
AI SOURCE: Tammy-Claude
WORKSTREAM: CARE
WORK ITEM: (Overlap) assessment-formulation-consistency
CONTRIBUTION TYPE: DECISION SUPPORT
EXISTING POSITION: as above
CONTRIBUTION: proposal to adopt one of the two levers (specification design or training design) as the primary route to calibration, based on Sources A and C
EVIDENCE/SOURCE: SYNTHETIC Sources A and C (External evidence)
SOURCE AUTHORITY: External evidence
EVIDENCE STRENGTH: Strong (A) / Moderate (C)
WHAT IS GENUINELY NEW: a forced choice between two routes that the existing position had not yet had to choose between
OVERLAP KEY: assessment-formulation-consistency
CLASSIFICATION: EXTENDS EXISTING
RECOMMENDED DISPOSITION: UPDATE EXISTING — only if a human accepts it
CONFIDENCE: Low — synthetic fixture evidence only, not real research
HUMAN DECISION REQUIRED: YES
TIMESTAMP: 2026-08-24T00:00:00Z
```

No write was made to `Existing Position`, `State`, `Human Decision`, `Proposed Merge`, or any Live Work Register `Current Position`/`Authority` for this disposition.

**PASS check:** `HUMAN DECISION REQUIRED: YES`. **PASS.**

---

## Test I — end-to-end

Traced in full for this run: SYNTHETIC Perplexity research (Sources A/B/C) → evidence validation gate (A validated, B rejected, C validated) → structured contributions (Tests A, F, H) → existing-work lookup (found the existing `assessment-formulation-consistency` Overlap Map entry and its three related Live Work Register items) → overlap detection (same `Overlap Key`, no new entry) → classification (`SUPPORTS EXISTING` / `CHALLENGES EXISTING` / `EXTENDS EXISTING`) → disposition (logged as evidence, one consequential disposition drafted but not applied) → human gate (`HUMAN DECISION REQUIRED: YES` retained throughout) → permitted persistence (one allowlisted write: `New Contribution` + `Sources`, via the Phase 5 write safety sequence — re-retrieved before writing, wrote only those two fields, read back, verified).

**PASS check:** all Phase 1–6 controls held throughout. **PASS.**

---

## Phase 6 regression (re-run after integration)

- **Source authority (ERO v7):** re-queried the full Live Work Register — ERO v7 still `Working draft`, Current Position unchanged, Authority Note unchanged. **PASS.**
- **Duplicate prevention / overlap:** Live Work Register item count unchanged at 8 before and after this run; Overlap Map still holds exactly the same two entries (`assessment-formulation-consistency`, `escalation-routing-consistency`) — no new item, no new overlap. **PASS.**
- **Human authority / blocklist:** no write in this run touched `Existing Position`, `Current Position`, `Decision Needed`, `Human Decision`, `State`/`Merge State`, or any `Authority` field on a real (non-fixture) record. **PASS.**
- **Read-back verification:** every write in this run (three Source Register creates, one Overlap Map update) was followed by a fetch/query confirming the persisted values. **PASS.**

No existing safety invariant was broken by the Perplexity integration.

---

## Summary

| Test | Result |
| --- | --- |
| A — fixture ingestion | PASS |
| B — weak source | PASS |
| C — provenance | PASS |
| D — deduplication | PASS |
| E — three-AI convergence | PASS |
| F — contradiction | PASS |
| G — local authority | PASS |
| H — human authority | PASS |
| I — end-to-end | PASS |

**Duplicate programme items created:** No — Live Work Register stayed at 8 items; Overlap Map stayed at 2 entries.
**Accepted programme state changed without a human decision:** No — `Existing Position`, `Current Position`, `State`, `Human Decision`, and every `Authority` field on real records are unchanged.
**Substantive programme state changed during testing:** Only additively and within the allowlist — three new Source Register entries (clearly marked SYNTHETIC TEST FIXTURE) and one `New Contribution`/`Sources` append on the real `assessment-formulation-consistency` Overlap Map entry. No `Current Position`, `Existing Position`, `Authority`, `Status`, `State`, or `Human Decision` field on any real record was altered.
**Test data remaining:** three Source Register pages tagged `SYNTHETIC TEST FIXTURE` (Source A: https://app.notion.com/3c6174d2d1ac81fc8783d53d9f55cc50, Source B: https://app.notion.com/3c6174d2d1ac815aa0eac5254413829e, Source C: https://app.notion.com/3c6174d2d1ac81ea8df9daadbfe51443), plus the appended synthetic-fixture text within the real Overlap Map entry's `New Contribution` field (left in place — it is provenance-tagged evidence logging, not a state change, and matches the "clearly retained as TEST data" stop condition). The Phase 5 TEST record (https://app.notion.com/3c6174d2d1ac81f8bb6eccae67bccf19) remains, still pending manual deletion.
