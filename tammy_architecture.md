# Tammy architecture

## Current architecture

`interface/server.py` is the existing browser/proxy boundary on port 4173. It serves the two-tab UI, forwards `/api/tammy` to the existing model runtime, and performs bounded read-only Notion retrieval for programme context. The repository-owned `backend/` service is a new additive state boundary on port 3001. It provides durable SQLite-backed operational state and health checks.

## Authority and provenance

Notion remains shared programme state. Git remains implementation state. The state service stores operational records but does not infer approval. A recommendation, agent output, or tracker row cannot become a human decision merely by being persisted.

## Phase 0 decisions

- SQLite first: durable, inspectable, zero infrastructure, and appropriate for a single-principal local Chief of Staff.
- Standard-library HTTP and SQLite first: the initial slice runs in a clean environment; framework dependencies can be introduced when the API surface stabilises.
- The existing UI/proxy remains intact while state becomes repository-owned and testable.
- External connectors will be bounded behind adapters and fail closed when credentials are absent.

## Implemented after Phase 0

The SQLite state service now stores workstreams, tasks, sources, artefacts, decisions, agents, proposed work orders, human gates, and events. Repository Markdown can be indexed through `/api/index`; authority is conservative: specifications are marked working draft, implementation briefs are marked controlled implementation brief, and other files remain unclassified. `/api/where-are-we` provides a bounded state summary with explicit repository provenance.

The proxy exposes `/api/state` and `/api/where-are-we` to the existing UI. The work rail consumes persistent tasks and fails closed when the state backend is unavailable; it does not reintroduce fixture data.

## Next slice

Expand the schema to include sources, artefacts, agents, work orders, events, and human gates; add migration/version handling; then connect `/api/state` to real Tab 2 state rather than demo panels.
