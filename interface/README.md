# Tammy v2 interface prototype

A standalone front-end prototype for the redesigned Tammy workbench.

## Run locally with live Tammy reasoning

Tammy v2 now proxies its centre workbench to the existing Tammy runtime at:

```text
http://127.0.0.1:3000/api/tammy
```

Start the existing Tammy runtime first and leave it running.

Then, from this repository root, run:

```bash
python3 interface/server.py
```

Open:

```text
http://localhost:4173
```

The v2 browser calls `/api/tammy` on port 4173. `server.py` forwards that request to the existing Tammy backend on port 3000, avoiding browser cross-origin issues.

To use another backend URL:

```bash
TAMMY_BACKEND_URL=http://127.0.0.1:3000/api/tammy python3 interface/server.py
```

No Python package install is required.

## What is live

- Analyse / Compare / Challenge / Decide prompts are sent to the existing Tammy runtime.
- Returned Tammy text is rendered in the central judgement card.
- API failures are shown explicitly rather than replaced with mock intelligence.

## What remains demo data

The following UI elements are deliberately labelled `DEMO` until they are wired to Notion retrieval:

- recent-work rail and summary counts;
- evidence/change/contradiction/decision cards;
- right-hand context rail;
- source lists, overlap counts and confidence indicator.

They must not be treated as live programme intelligence yet.

## Visual system

- Midnight-blue and soft-gold visual system.
- Three-column workbench: work navigation, Tammy workspace, context rail.
- Explicit authority/status cues such as `WORKING DRAFT`.
- Responsive layout for narrower screens.

## Architectural boundary

This interface does not replace or weaken the v1 programme-intelligence controls. Source authority, human-decision gates, write-back restrictions, stale-state protection and provenance remain governed by the existing v1 specification.

The next connection step is the right-hand context rail: populate it from bounded Notion retrieval rather than fixture data.
