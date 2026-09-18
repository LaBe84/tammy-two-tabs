"""Unified provenance-aware retrieval service.

Combines GitHub, Notion, and SQLite sources with explicit authority labelling
and provenance tracking. Implements Phase 3 of the persistent state layer.

Key invariants:
- Retrieval is bounded and relevance-driven, never exhaustive
- All sources are explicitly labelled with authority state
- EVIDENCE UNAVAILABLE on failure, never fabricated current state
- Read-only unless explicitly authorised
- Repository, Notion, and SQLite state remain distinguishable
"""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


class Authority:
    """Authority states for all material sources."""
    CONTROLLED_CURRENT = "controlled current"
    CONCEPTUAL_DEVELOPMENT = "conceptual development"
    WORKING_DRAFT = "working draft"
    EXTERNAL_EVIDENCE = "external evidence"
    ARCHIVED = "archived"
    UNCLASSIFIED = "unclassified"


class EpistemicStatus:
    """Distinguishes evidence, inference, unknown, recommendation, proposal."""
    EVIDENCE = "evidence"
    INFERENCE = "inference"
    UNKNOWN = "unknown"
    RECOMMENDATION = "recommendation"
    PROPOSAL = "proposal"
    HUMAN_DECISION = "human decision"


def now():
    """ISO 8601 timestamp (UTC)."""
    return datetime.now(timezone.utc).isoformat()


class ProvenanceAwareRetrieval:
    """Single entry point for grounded context retrieval across all sources."""

    def __init__(self, store, notion_retriever=None, github_retriever=None):
        """
        Initialize retrieval service.

        Args:
            store: SQLite Store instance for repository state
            notion_retriever: Optional Notion retrieval callable
            github_retriever: Optional GitHub retrieval callable
        """
        self.store = store
        self.notion_retriever = notion_retriever
        self.github_retriever = github_retriever

    def _label_source(
        self,
        data: Dict[str, Any],
        source: str,
        authority: str,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Attach provenance labels to a retrieved item."""
        return {
            **data,
            "_source": source,
            "_authority": authority,
            "_location": location or "unknown",
            "_retrieved_at": now(),
            "_read_only": True,
        }

    def retrieve_repository_state(self, query: str = "", limit: int = 20) -> Dict[str, Any]:
        """
        Retrieve state from the local SQLite persistence layer.

        Repository state includes:
        - Active workstreams and tasks
        - Work orders and delegations
        - Decisions and human gates
        - Indexed repository artefacts

        Args:
            query: Optional search query
            limit: Result limit per entity type

        Returns:
            Labelled, bounded repository state
        """
        try:
            raw_state = self.store.search(query) if query else self.store.list_state()

            # Apply limit per entity type
            limited = {
                key: items[:limit]
                for key, items in raw_state.items()
                if isinstance(items, list)
            }

            return {
                "source": "repository",
                "authority": Authority.CONTROLLED_CURRENT,
                "description": "Local repository operational state from SQLite",
                "retrieved_at": now(),
                "read_only": True,
                "data": limited,
            }
        except Exception as exc:
            return {
                "source": "repository",
                "state": "UNAVAILABLE",
                "error": str(exc),
                "retrieved_at": now(),
            }

    def retrieve_notion_context(self, query: str, mode: str = "Analyse") -> Dict[str, Any]:
        """
        Retrieve bounded Notion programme context.

        Wraps the existing Notion retrieval (live_work, sources, overlaps).
        Authority is NOT inferred from Notion presence—each item carries
        its own Authority value from the Notion schema.

        Args:
            query: User request for scoping
            mode: "Analyse", "Compare", "Challenge", "Decide"

        Returns:
            Labelled Notion context or EVIDENCE UNAVAILABLE
        """
        if not self.notion_retriever:
            return {
                "source": "notion",
                "state": "UNAVAILABLE",
                "reason": "Notion retriever not configured",
                "retrieved_at": now(),
            }

        try:
            context = self.notion_retriever(query, mode)
            # Each item in context carries its own Authority from Notion schema
            return {
                "source": "notion",
                "authority": Authority.UNCLASSIFIED,  # Per-item authorities vary
                "description": "Shared Lifeline programme state (read-only, bounded)",
                "retrieved_at": context.get("meta", {}).get("retrieved_at", now()),
                "read_only": context.get("meta", {}).get("read_only", True),
                "bounded": context.get("meta", {}).get("bounded", True),
                "query_scope": context.get("meta", {}).get("query_scope", []),
                "registers_queried": context.get("meta", {}).get("registers_queried", []),
                "work_items": [
                    self._label_source(
                        item,
                        "notion",
                        item.get("Authority", Authority.UNCLASSIFIED),
                        item.get("Notion URL"),
                    )
                    for item in context.get("work_items", [])
                ],
                "sources": [
                    self._label_source(
                        item,
                        "notion",
                        item.get("Authority", Authority.UNCLASSIFIED),
                        item.get("Notion URL"),
                    )
                    for item in context.get("sources", [])
                ],
                "overlaps": [
                    self._label_source(
                        item,
                        "notion",
                        Authority.UNCLASSIFIED,  # Overlap authority varies by merge state
                        item.get("Notion URL"),
                    )
                    for item in context.get("overlaps", [])
                ],
            }
        except Exception as exc:
            return {
                "source": "notion",
                "state": "UNAVAILABLE",
                "error": str(exc),
                "retrieved_at": now(),
            }

    def retrieve_github_context(
        self, workstream: str = "", task_keyword: str = ""
    ) -> Dict[str, Any]:
        """
        Retrieve bounded GitHub context (repository metadata, relevant issues/PRs).

        Authority of GitHub issues/PRs is UNCLASSIFIED unless they reference
        a controlled source or decision.

        Args:
            workstream: Optional workstream filter
            task_keyword: Optional search term

        Returns:
            Labelled GitHub context or EVIDENCE UNAVAILABLE
        """
        if not self.github_retriever:
            return {
                "source": "github",
                "state": "UNAVAILABLE",
                "reason": "GitHub retriever not configured",
                "retrieved_at": now(),
            }

        try:
            context = self.github_retriever(workstream, task_keyword)
            return {
                "source": "github",
                "authority": Authority.UNCLASSIFIED,
                "description": "Repository implementation state and issues",
                "retrieved_at": now(),
                "read_only": True,
                "bounded": True,
                "issues": [
                    self._label_source(item, "github", Authority.UNCLASSIFIED)
                    for item in context.get("issues", [])
                ],
                "pull_requests": [
                    self._label_source(item, "github", Authority.UNCLASSIFIED)
                    for item in context.get("pull_requests", [])
                ],
            }
        except Exception as exc:
            return {
                "source": "github",
                "state": "UNAVAILABLE",
                "error": str(exc),
                "retrieved_at": now(),
            }

    def where_are_we(self, query: str = "") -> Dict[str, Any]:
        """
        Unified "Where are we?" synthesis from all sources.

        Answers:
        - Current position (from repository and Notion state)
        - Completed work (from repository tasks and Notion work items)
        - Outstanding work (open tasks, pending decisions)
        - Blockers (tasks with blocked_by, human gates, unavailable evidence)
        - Dependencies
        - Decisions required
        - Evidence gaps
        - Contradictions (from repository and Notion)
        - Recommended next actions
        - Provenance (explicitly labelled per item)
        - Uncertainty (failures, unavailable state, conflicting authorities)

        Args:
            query: Optional workstream/task filter

        Returns:
            Grounded synthesis object with full provenance
        """
        repo_state = self.retrieve_repository_state(query, limit=50)
        notion_context = self.retrieve_notion_context(query, "Analyse")
        github_context = self.retrieve_github_context()

        # Extract high-level summary
        repo_data = repo_state.get("data", {})
        notion_data = notion_context.get("work_items", [])

        open_tasks = [
            t
            for t in repo_data.get("tasks", [])
            if t.get("status") not in ("closed", "completed")
        ]
        completed_tasks = [
            t
            for t in repo_data.get("tasks", [])
            if t.get("status") in ("closed", "completed")
        ]
        blocked_tasks = [t for t in open_tasks if t.get("blocked_by")]
        decisions_needed = [
            d
            for d in repo_data.get("decisions", [])
            if d.get("status") in ("proposed", "open")
        ]
        human_gates_pending = [
            g for g in repo_data.get("human_gates", []) if g.get("status") == "required"
        ]

        # Identify evidence gaps
        evidence_unavailable = []
        if notion_context.get("state") == "UNAVAILABLE":
            evidence_unavailable.append({
                "type": "programme_context",
                "reason": notion_context.get("error", "Notion retrieval failed"),
                "impact": "Programme state and overlap detection unavailable",
            })
        if github_context.get("state") == "UNAVAILABLE":
            evidence_unavailable.append({
                "type": "github_context",
                "reason": github_context.get("error", "GitHub retrieval failed"),
                "impact": "Repository implementation state unavailable",
            })

        return {
            "epistemic_status": "synthesis_from_persistent_state",
            "retrieved_at": now(),
            "query": query,
            "provenance": {
                "repository_state": repo_state,
                "notion_context": notion_context,
                "github_context": github_context,
            },
            "summary": {
                "workstreams": len(repo_data.get("workstreams", [])),
                "open_tasks": len(open_tasks),
                "completed_tasks": len(completed_tasks),
                "blocked_tasks": len(blocked_tasks),
                "decisions_required": len(decisions_needed),
                "human_gates_pending": len(human_gates_pending),
                "evidence_gaps": len(evidence_unavailable),
            },
            "current_position": {
                "open_tasks": open_tasks[:10],
                "completed_tasks": completed_tasks[:5],
            },
            "outstanding_work": {
                "open_tasks": open_tasks[:20],
                "decisions_needed": decisions_needed[:10],
                "work_orders_pending": [
                    w
                    for w in repo_data.get("work_orders", [])
                    if w.get("status") == "proposed"
                ][:10],
            },
            "blockers": {
                "blocked_tasks": blocked_tasks,
                "human_gates_pending": human_gates_pending,
                "unavailable_evidence": evidence_unavailable,
            },
            "decisions_required": decisions_needed[:10],
            "next_actions": [
                {
                    "priority": "highest",
                    "type": "human_decision",
                    "count": len(human_gates_pending),
                    "reason": "Pending human decisions block progress",
                }
                if human_gates_pending
                else {
                    "priority": "high",
                    "type": "blocked_task_unblock",
                    "count": len(blocked_tasks),
                    "reason": "Resolve blocker relationships",
                }
                if blocked_tasks
                else {
                    "priority": "normal",
                    "type": "complete_open_task",
                    "count": len(open_tasks),
                    "reason": "Continue active work",
                },
            ],
            "uncertainty": {
                "programme_state_available": notion_context.get("state") != "UNAVAILABLE",
                "repository_state_available": repo_state.get("state") != "UNAVAILABLE",
                "github_state_available": github_context.get("state") != "UNAVAILABLE",
                "gaps": evidence_unavailable,
            },
        }
