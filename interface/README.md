# Tammy v2 programme-intelligence workbench

A local three-column workbench with live Tammy reasoning and bounded, read-only retrieval from the three controlled Notion registers.

## Run locally with live Tammy reasoning

Tammy v2 now proxies its centre workbench to the existing Tammy runtime at:

```text
http://127.0.0.1:3000/api/tammy
```

Start the existing Tammy runtime first and leave it running. It must listen on port 3000.

The interface accepts a Notion integration token from any one of these environment variables:

- `TAMMY_NOTION_TOKEN`
- `NOTION_TOKEN`
- `NOTION_API_KEY`
- `NOTION_INTEGRATION_TOKEN`

The Notion integration must have read access to:

- Tammy — Live Work Register
- Tammy — Source Register
- Tammy — Overlap Map

Then, from this repository root, run the bridge in a shell where the token is already set:

```bash
TAMMY_BACKEND_URL=http://127.0.0.1:3000/api/tammy python3 interface/server.py
```

Open:

```text
http://localhost:4173
```

The v2 browser calls `/api/tammy` on port 4173. `server.py` forwards that request to the existing Tammy backend on port 3000, avoiding browser cross-origin issues.

If the token is already stored in the runtime project's `.env.local`, load that file into the shell without printing it, then start the bridge:

```bash
set -a
source "/path/to/runtime/.env.local"
set +a
TAMMY_BACKEND_URL=http://127.0.0.1:3000/api/tammy python3 interface/server.py
```

No Python package install is required.

## What is live

- Analyse / Compare / Challenge / Decide prompts are sent to the existing Tammy runtime.
- Returned Tammy text is rendered in the central judgement card.
- Before each request, the interface queries only the relevant Notion registers and injects the returned programme metadata into Tammy's task.
- The right context rail displays retrieved work items, source authority and unresolved overlap state.
- The left rail displays the bounded set of relevant, non-resolved work items.
- API failures are shown explicitly rather than replaced with mock intelligence.

## Retrieval boundary

- Uses Notion API version `2026-03-11` and the data-source query endpoint.
- Queries are capped at 8 Live Work records, 6 Source records and 5 Overlap records.
- Workstream terms in the current request narrow the database filters.
- Source records are retrieved only when the task needs evidence or authority.
- Full Notion page content is never requested.
- Only selected register properties are returned to the browser and Tammy runtime.
- No Notion create, update, archive or delete route exists in the interface.
- If retrieval fails, the interface reports programme context as unavailable and never substitutes cached state.

Check configuration without reading a register:

```bash
curl -sS http://127.0.0.1:4173/api/context/health
```

Run a bounded retrieval test:

```bash
curl -sS -X POST http://127.0.0.1:4173/api/context \
  -H 'Content-Type: application/json' \
  -d '{"query":"Compare the CARE Log and secondary assessment authority","mode":"Compare"}'
```

## Visual system

- Midnight-blue and soft-gold visual system.
- Three-column workbench: work navigation, Tammy workspace, context rail.
- Explicit authority/status cues such as `WORKING DRAFT`.
- Responsive layout for narrower screens.

## Architectural boundary

This interface does not replace or weaken the v1 programme-intelligence controls. Source authority, human-decision gates, write-back restrictions, stale-state protection and provenance remain governed by the existing v1 specification.

Presence in Notion is not approval. The runtime receives every retrieved record with its explicit `Authority` or `Human Decision` field, and its prompt requires those states to be preserved.
