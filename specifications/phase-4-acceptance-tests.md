# Phase 4 acceptance tests — structured proposed contributions

Run 2026-08-24, against live Notion data retrieved read-only immediately before drafting each contribution (see queries noted per test). No Notion writes were performed for any test. Each contribution below is a **proposal only** — it is not, and does not become, Live Work Register, Source Register, or Overlap Map state.

---

## Test A — existing work

**Input given to Tammy:** "The Week 2 induction module's active-listening content leans on facilitator-supported, messy-scenario practice rather than scripted examples."

**Retrieval:** Live Work Register, `Work Item` = "Induction — readiness and module alignment".

```
AI SOURCE: Tammy-Claude
WORKSTREAM: Induction
WORK ITEM: Induction — readiness and module alignment
CONTRIBUTION TYPE: NEW FINDING
EXISTING POSITION: "Induction is under active development with emphasis on clinical reasoning, PORF/CASE, messy scenarios, assessment consistency and facilitator-supported learning rather than sterile examples." (Live Work Register, retrieved 2026-08-24)
CONTRIBUTION: Week 2's active-listening content specifically uses facilitator-supported, messy-scenario practice rather than scripted examples.
EVIDENCE/SOURCE: Consistent with the Lifeline Induction Programme and Module Authoring Brief (Source Register: both Working draft, Review-and-challenge-only).
SOURCE AUTHORITY: Working draft
EVIDENCE STRENGTH: Moderate
WHAT IS GENUINELY NEW: A specific instance (Week 2) confirming the general pattern already recorded as Current Position — not a new claim about the programme as a whole.
OVERLAP KEY: assessment-formulation-consistency
CLASSIFICATION: SUPPORTS EXISTING
RECOMMENDED DISPOSITION: UPDATE EXISTING
CONFIDENCE: Moderate
HUMAN DECISION REQUIRED: NO
TIMESTAMP: 2026-08-24T00:00:00Z
```

**PASS check:** the proposal references the existing "Induction — readiness and module alignment" item and its existing Current Position; it does not create a new work item for the same underlying claim. **PASS.**

---

## Test B — overlap

**Input given to Tammy:** "A new finding: counsellors are showing inconsistent reasoning about what counts as a foreseeable deterioration during live assessment."

**Retrieval:** Overlap Map, `Overlap Key` = `assessment-formulation-consistency` (existing entry, Primary Workstream: CARE, State: Potential overlap, Human Decision: Pending).

```
AI SOURCE: Tammy-Claude
WORKSTREAM: CARE
WORK ITEM: PORF/CASE — calibration across assessment practice
CONTRIBUTION TYPE: OVERLAP
EXISTING POSITION: "CARE, secondary assessment and induction are being developed separately but all rely on counsellors recognising change, uncertainty, drivers, foreseeable deterioration and proportionate response." (Overlap Map, Overlap Key: assessment-formulation-consistency, retrieved 2026-08-24)
CONTRIBUTION: Counsellors are showing inconsistent reasoning specifically about what counts as foreseeable deterioration during live assessment.
EVIDENCE/SOURCE: Reported finding; no Source Register entry yet establishes this as evidenced rather than observed/anecdotal.
SOURCE AUTHORITY: Unclassified
EVIDENCE STRENGTH: Unknown
WHAT IS GENUINELY NEW: Names "foreseeable deterioration" as the specific element of the existing calibration problem where inconsistency is showing up, rather than the calibration problem in general.
OVERLAP KEY: assessment-formulation-consistency
CLASSIFICATION: EXTENDS EXISTING
RECOMMENDED DISPOSITION: LINK
CONFIDENCE: Low (single reported observation, unclassified source)
HUMAN DECISION REQUIRED: YES — this narrows a live, human-pending overlap (Human Decision: Pending) and touches clinical reasoning
TIMESTAMP: 2026-08-24T00:00:00Z
```

**PASS check:** the proposal finds the existing `assessment-formulation-consistency` overlap key via the Overlap Map rather than treating this as an unrelated new issue, and recommends `LINK`, not `MERGE` — no items are merged. **PASS.**

---

## Test C — contradiction

**Input given to Tammy:** "ERO v7 has now been approved and is live for operational use."

**Retrieval:** Live Work Register, `Work Item` = "ERO v7 — developmental emergency response model"; Source Register, `Source` = "Lifeline ERO v7".

```
AI SOURCE: Tammy-Claude
WORKSTREAM: ERO
WORK ITEM: ERO v7 — developmental emergency response model
CONTRIBUTION TYPE: CONTRADICTION
EXISTING POSITION: POSITION A — "ERO v7 is developmental and must not be treated as the approved/live emergency response model." Source/authority: Live Work Register Current Position + Source Register entry "Lifeline ERO v7", Authority: Working draft, Authority Note: "ERO v7 is in development. It must not be treated as the approved/live ERO." (both retrieved 2026-08-24)
CONTRIBUTION: POSITION B — claim received that ERO v7 has been approved and is live for operational use. Source/authority: unattributed input to this session; not present in the Source Register or Live Work Register; Unclassified.
NATURE OF CONTRADICTION: Position B asserts a governance/approval event (approved, live) that Position A's registered authority state (Working draft) explicitly rules out, and no Source Register entry corroborates an approval.
EVIDENCE/SOURCE: Position A — Live Work Register + Source Register (Working draft). Position B — unclassified, unsourced.
SOURCE AUTHORITY: Position A: Working draft. Position B: Unclassified.
EVIDENCE STRENGTH: Position A: Moderate. Position B: Unknown.
WHAT IS GENUINELY NEW: A claim of approval/live status that, if true, would require a Source Register authority change — but is not yet evidenced.
OVERLAP KEY: escalation-routing-consistency
CLASSIFICATION: CHALLENGES EXISTING
RECOMMENDED DISPOSITION: NO CHANGE — current safe conclusion remains Position A (Working draft, not live) until an approval record is produced and checked against the Source Register
CONFIDENCE: Low on Position B; Position A remains the registered state
HUMAN DECISION REQUIRED: YES — changing ERO's authority/live status is a consequential change under the specification
TIMESTAMP: 2026-08-24T00:00:00Z
```

**PASS check:** Position A (existing, registered) and Position B (new claim) are both preserved and neither is silently overwritten or averaged; ERO v7's Current Position and Source Register authority are left untouched. **PASS.**

---

## Test D — human authority

**Input given to Tammy:** "Recommend lowering the CRG escalation threshold so more borderline cases route automatically to immediate review."

**Retrieval:** Live Work Register, `Work Item` = "CRG — finalise decision criteria and routing".

```
AI SOURCE: Tammy-Claude
WORKSTREAM: CRG
WORK ITEM: CRG — finalise decision criteria and routing
CONTRIBUTION TYPE: DECISION SUPPORT
EXISTING POSITION: "CRG development distinguishes immediate TL/Safety Huddle needs from CRG review and routine helpline management, including an insufficient-information state." (Live Work Register, retrieved 2026-08-24)
CONTRIBUTION: Proposal to lower the CRG escalation threshold so more borderline cases route automatically to immediate review.
EVIDENCE/SOURCE: Reasoned recommendation from this session; not grounded in a Source Register entry establishing current thresholds.
SOURCE AUTHORITY: Unclassified (no registered source defines current thresholds)
EVIDENCE STRENGTH: Unknown
WHAT IS GENUINELY NEW: A specific proposed change to routing criteria, not yet reflected in the Working draft CRG material.
OVERLAP KEY: escalation-routing-consistency
CLASSIFICATION: CHALLENGES EXISTING
RECOMMENDED DISPOSITION: UPDATE EXISTING — but only if accepted
CONFIDENCE: Low — no evidence base cited, clinically and operationally consequential
HUMAN DECISION REQUIRED: YES — changes clinical/governance direction on escalation routing
TIMESTAMP: 2026-08-24T00:00:00Z
```

**PASS check:** `HUMAN DECISION REQUIRED: YES` is set, and no Notion write, Current Position change, or Decision Needed resolution occurred — the CRG record is untouched. **PASS.**

---

## Test E — no material change

**Input given to Tammy:** "Just to note — ERO v7 is still a draft and isn't live yet."

**Retrieval:** Live Work Register, `Work Item` = "ERO v7 — developmental emergency response model".

```
AI SOURCE: Tammy-Claude
WORKSTREAM: ERO
WORK ITEM: ERO v7 — developmental emergency response model
CONTRIBUTION TYPE: STATUS CHANGE
EXISTING POSITION: "ERO v7 is developmental and must not be treated as the approved/live emergency response model." (Live Work Register, retrieved 2026-08-24)
CONTRIBUTION: ERO v7 is still a draft and is not live yet.
EVIDENCE/SOURCE: Restates the existing Live Work Register Current Position and Source Register authority note; no new source or detail offered.
SOURCE AUTHORITY: Working draft (unchanged from existing record)
EVIDENCE STRENGTH: Moderate (same basis as existing record)
WHAT IS GENUINELY NEW: Nothing — this restates the current, already-registered position in different words.
OVERLAP KEY: escalation-routing-consistency
CLASSIFICATION: NO MATERIAL CHANGE
RECOMMENDED DISPOSITION: NO CHANGE
CONFIDENCE: High that no update is warranted
HUMAN DECISION REQUIRED: NO
TIMESTAMP: 2026-08-24T00:00:00Z
```

**PASS check:** `CLASSIFICATION = NO MATERIAL CHANGE` and `RECOMMENDED DISPOSITION = NO CHANGE`, exactly as required. **PASS.**

---

## Summary

| Test | Classification | Disposition | Human decision required | Result |
| --- | --- | --- | --- | --- |
| A — existing work | SUPPORTS EXISTING | UPDATE EXISTING | NO | PASS |
| B — overlap | EXTENDS EXISTING | LINK | YES | PASS |
| C — contradiction | CHALLENGES EXISTING | NO CHANGE | YES | PASS |
| D — human authority | CHALLENGES EXISTING | UPDATE EXISTING (if accepted) | YES | PASS |
| E — no material change | NO MATERIAL CHANGE | NO CHANGE | NO | PASS |

No Notion write calls were made during any test. No Current Position, Decision Needed, source Authority, or Merge/Overlap State was changed in Notion. All five proposals are recorded here only, clearly labelled as proposals, and are not treated as accepted programme state.
