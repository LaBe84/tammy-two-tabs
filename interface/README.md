# Tammy v2 interface prototype

A standalone front-end prototype for the redesigned Tammy workbench.

## Run locally

From the repository root:

```bash
python3 -m http.server 4173 --directory interface
```

Then open:

```text
http://localhost:4173
```

No install step is required.

## What is implemented

- Midnight-blue and soft-gold visual system.
- Three-column workbench: work navigation, Tammy workspace, live-context rail.
- Analyse / Compare / Challenge / Decide interaction modes.
- Recent-work selection.
- Expandable judgement card.
- Responsive layout for narrower screens.
- Explicit authority/status cues such as `WORKING DRAFT`.

## Deliberate boundary

This branch is the interface prototype only. It does **not** yet connect the browser directly to Notion, OpenAI, Perplexity, or the v1 Tammy intelligence layer. The command box therefore demonstrates the interaction model without reading or writing programme state.

The next implementation step, after visual approval, is to connect this interface to the existing intelligence layer without changing its source-authority, human-decision, write-back, or provenance controls.
