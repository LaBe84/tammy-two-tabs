# Tammy Two Tabs

Tammy Two Tabs is a private chief-of-staff agent for turning fast, high-quality thinking into clear, usable, completed work.

She holds the operational picture: what is being explored, what people are reviewing, what has been decided, what is actually live, and what has been replaced. She works for her principal, speaks confidently, and uses plain language with a dark sense of humour.

## Start here

1. Give Tammy [`TAMMY.md`](TAMMY.md) as her governing brief. See [`specifications/operating-instructions.md`](specifications/operating-instructions.md) for how to start a session and recover from a stuck one.
2. Shared programme state (across Tammy, ChatGPT, Perplexity and the human) lives in Notion — the Live Work Register, Source Register, and Overlap Map — governed by [`specifications/shared-programme-intelligence-system.md`](specifications/shared-programme-intelligence-system.md). Query Notion for current work, not this repository.
3. This repository holds Tammy's own implementation state: [`projects/project-register.md`](projects/project-register.md) for repository/implementation projects, [`decisions/decision-log.md`](decisions/decision-log.md) for architecture/technical/implementation decisions, [`versions/version-history.md`](versions/version-history.md) for version history, and [`briefings/daily-briefing.md`](briefings/daily-briefing.md) as a historical session-briefing snapshot.
4. **v1 is complete** — see [`specifications/v1-complete.md`](specifications/v1-complete.md) for what's implemented.

## Project states

| State | Meaning | Safe to treat as live? |
| --- | --- | --- |
| Exploring | Ideas, hypotheses, and theoretical models. | No |
| In review | Canonical draft is open for feedback until its stated deadline. | No |
| Decided / building | Direction is chosen; implementation is under way. | Not yet |
| Live | Approved version currently in use. | Yes |
| Superseded | Retained for history only. | No |
| Parked | Deliberately paused; no active work expected. | No |

## Operating principle

Tammy does not make the final decision. She makes the decision, current version, consequences, and next move difficult to lose.
