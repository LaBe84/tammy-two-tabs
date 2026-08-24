# Operating instructions (Phase 8)

## Specification/repository conflict flagged first

Phase 8 asked for startup instructions including "exact command," "expected localhost address," an OpenAI API health check, and OpenAI-specific failure diagnostics.

- **SPECIFICATION REQUIREMENT:** document a running application with a localhost address, an OpenAI API, and a UI that can hang independently of that API.
- **CURRENT REPOSITORY CONSTRAINT:** this repository contains no application code, no server, no UI, and no OpenAI integration (confirmed: no `package.json`, no server entry point, no OpenAI references anywhere in the repo). Tammy is not a deployed app in v1 — she is a governing brief (`TAMMY.md`) read by an LLM agent session (this has been Claude Code, via the Claude API/Notion MCP connector, throughout Phases 1–7), with Notion as the shared-state backend.
- **WHY THEY CONFLICT:** there is nothing to start on a port, and no OpenAI key to check, because v1 was never built as that kind of system.
- **SMALLEST PROPOSED CHANGE:** document the startup/recovery/config Tammy v1 actually has (below) instead of inventing a server, port, or OpenAI dependency that doesn't exist.
- **HUMAN DECISION REQUIRED:** only if a running Tammy application (server + UI + OpenAI integration) is wanted for a future version — that would be new scope, out of bounds for Phase 8 ("do not add new capabilities").

The rest of this document covers the real system.

## Start Tammy

Tammy has no server process and no localhost address in v1. "Starting" Tammy means opening an LLM agent session against this repository with the Notion connector available.

1. Have this repository checked out (or open as a Claude Code on the web session sourced from it).
2. Give the agent `TAMMY.md` as its governing brief (Claude Code sessions do this automatically when it's present in the repo root; other harnesses should be pointed at it explicitly).
3. Confirm the session's Notion connector/MCP server has access to the three databases named in [`shared-programme-intelligence-system.md`](shared-programme-intelligence-system.md): Live Work Register, Source Register, Overlap Map.
4. Begin the session. Per `TAMMY.md`'s "Opening a session" section, Tammy should retrieve relevant Notion state and give an operational briefing rather than wait passively.

## Stop Tammy

End the agent session normally (close the Claude Code session / end the conversation). There is no separate process to shut down and no state held outside Notion and this repository, so there is nothing that needs a clean shutdown sequence.

## If Tammy does not load

1. Confirm the repository is checked out and `TAMMY.md` is present and readable.
2. Confirm the agent harness actually loaded `TAMMY.md` as the system/governing prompt (check the session's stated role — it should describe itself as Tammy Two Tabs, not a generic assistant).
3. Run the Notion connectivity test below. If it fails, Tammy will still "load" as an agent but cannot retrieve shared programme state — she should say so explicitly rather than proceed as if Notion is reachable (see `shared-programme-intelligence-system.md`, Failure behaviour).

## If Tammy "hangs"

There is no separate UI process in v1, so a hang is one of two things — tell them apart before troubleshooting:

- **Host chat client is slow/unresponsive:** the agent harness (Claude Code, claude.ai, etc.) itself is not rendering or responding. This is a host-application issue, not a Tammy issue — restart or reload the host client.
- **A tool call is pending:** Tammy is waiting on a Notion (or other) tool call — usually visible as an in-progress tool-use indicator in the session. This is expected latency, not a hang, unless it exceeds the connector's own timeout. If a Notion query specifically stalls, see "if Notion fails" below — the workspace `Query Data Source` (SQL) tool has a usage limit (observed during Phase 6) that can cause repeated failures rather than a hang; `fetch` and view-mode queries are not subject to the same limit and are the fallback.

## Test connectivity

The known-safe, side-effect-free check is fetching the connected workspace identity, which touches no programme data:

```
notion-fetch(id: "self")
```

This returns the connected Notion workspace and the authenticated user, and confirms the connector is live without reading or writing any Live Work Register, Source Register, or Overlap Map content.

## If Notion fails

- **How Tammy should behave:** state plainly that shared programme state could not be retrieved. Do not substitute cached or general knowledge as if it were current Notion state. Continue only with what can be safely answered without it (see `shared-programme-intelligence-system.md`, Failure behaviour, and the AA section of the original v1 spec).
- **Minimal diagnostic:** run the connectivity test above (`notion-fetch(id: "self")`). If it fails, check: (a) the MCP/connector session status in the host harness, (b) whether the failure is a hard connection error vs. a workspace usage-limit error (Phase 6 hit a `Query Data Source` usage limit specifically — that is a rate limit, not an outage, and `fetch`/view-mode queries remain available as a fallback), (c) whether the three database URLs recorded in `shared-programme-intelligence-system.md` are still valid and still shared with the connected integration.

## Configuration

| Setting | Required/Optional/Dev-only | Notes |
| --- | --- | --- |
| Notion MCP connector, connected and granted access to the three Tammy databases (Live Work Register, Source Register, Overlap Map) | **Required** | Without it, Tammy can still operate on repository content (this file set) but cannot retrieve or write shared programme state. |

No other configuration or environment variables are used by this repository — there is no `.env` file, no server configuration, and no other integration (OpenAI or otherwise) referenced anywhere in v1. This table lists everything actually in use; nothing has been invented for completeness. If a future version adds real configuration (an app, a different LLM provider, additional connectors), this table is the place to record it — do not assume anything beyond what's listed here is already wired up.
