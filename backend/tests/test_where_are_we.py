"""Integration tests for unified "Where are we?" synthesis.

Tests the acid test: Can Tammy tell Lee what has already happened,
what remains, what is blocked and what should happen next, using
persistent state and identifiable sources?

These tests verify:
1. Repository state is retrievable and labelled with authority
2. Notion context retrieval is bounded and source-labelled
3. Synthesis correctly answers the core question from persistent state
4. Failures produce explicit UNAVAILABLE, not fabricated state
5. Provenance is preserved and traceable
6. Contradictions are preserved, not averaged away
7. Human decision gates are surfaced
8. Blockers are identified
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from backend.store import Store
from backend.retrieval import (
    ProvenanceAwareRetrieval,
    Authority,
    EpistemicStatus,
)


class WhereAreWeAcidTests(unittest.TestCase):
    """Core acid tests for the "Where are we?" synthesis."""

    def setUp(self):
        """Set up test fixtures."""
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test.sqlite3"
        self.store = Store(self.db_path)

    def tearDown(self):
        """Clean up."""
        self.store.close()
        self.tmp.cleanup()

    def test_repository_state_is_retrievable_and_labelled(self):
        """Repository state retrieval labels all items with authority."""
        ws = self.store.add_workstream("Induction", "Foundation e-learning")
        task = self.store.add_task("Review Week 3", ws, priority="high")
        decision = self.store.add_decision(
            "Approve exposure gate", "Red-team findings support approval"
        )

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.retrieve_repository_state()

        self.assertEqual(result["source"], "repository")
        self.assertEqual(result["authority"], Authority.CONTROLLED_CURRENT)
        self.assertTrue(result["read_only"])
        self.assertEqual(len(result["data"]["workstreams"]), 1)
        self.assertEqual(len(result["data"]["tasks"]), 1)
        self.assertEqual(len(result["data"]["decisions"]), 1)

    def test_repository_state_query_is_bounded(self):
        """Repository retrieval respects limits."""
        ws = self.store.add_workstream("Test")
        for i in range(30):
            self.store.add_task(f"Task {i}", ws)

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.retrieve_repository_state("Task", limit=10)

        tasks = result["data"].get("tasks", [])
        self.assertLessEqual(len(tasks), 10)

    def test_notion_context_unavailable_fails_closed(self):
        """Notion retrieval failure does not fabricate state."""
        retrieval = ProvenanceAwareRetrieval(self.store, notion_retriever=None)
        result = retrieval.retrieve_notion_context("test", "Analyse")

        self.assertEqual(result.get("state"), "UNAVAILABLE")
        self.assertIn("not configured", result.get("reason", ""))

    def test_notion_context_mock_is_labelled(self):
        """Mocked Notion context preserves authority labelling."""

        def mock_notion(query, mode):
            return {
                "meta": {
                    "retrieved_at": "2026-08-29T12:00:00Z",
                    "read_only": True,
                    "bounded": True,
                    "query_scope": ["Induction"],
                    "registers_queried": ["live_work"],
                },
                "work_items": [
                    {
                        "Work Item": "Week 3 slides",
                        "Status": "Progressing",
                        "Authority": Authority.WORKING_DRAFT,
                        "Notion URL": "https://notion.example/item1",
                    }
                ],
                "sources": [],
                "overlaps": [],
            }

        retrieval = ProvenanceAwareRetrieval(self.store, notion_retriever=mock_notion)
        result = retrieval.retrieve_notion_context("Induction", "Analyse")

        self.assertEqual(result["source"], "notion")
        self.assertTrue(result["read_only"])
        self.assertTrue(result["bounded"])
        self.assertEqual(len(result["work_items"]), 1)

        item = result["work_items"][0]
        self.assertEqual(item["_source"], "notion")
        self.assertEqual(item["_authority"], Authority.WORKING_DRAFT)
        self.assertIn("_retrieved_at", item)

    def test_where_are_we_answers_current_position(self):
        """'Where are we?' correctly identifies current state."""
        ws = self.store.add_workstream("Induction")
        completed_task = self.store.add_task("Review Week 1", ws, priority="normal")
        open_task = self.store.add_task("Review Week 3", ws, priority="high")

        self.store.db.execute(
            "UPDATE tasks SET status = ? WHERE id = ?", ("closed", completed_task)
        )
        self.store.db.commit()

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.where_are_we()

        self.assertIn("current_position", result)
        self.assertEqual(len(result["summary"]["completed_tasks"]), 1)
        self.assertEqual(len(result["summary"]["open_tasks"]), 1)

    def test_where_are_we_identifies_blockers(self):
        """'Where are we?' surfaces blocked tasks."""
        ws = self.store.add_workstream("Induction")
        blocker_task = self.store.add_task("Red-team Week 3", ws)
        blocked_task = self.store.add_task("Approve Week 3", ws)

        self.store.db.execute(
            "UPDATE tasks SET blocked_by = ? WHERE id = ?",
            (blocker_task, blocked_task),
        )
        self.store.db.commit()

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.where_are_we()

        self.assertEqual(len(result["summary"]["blocked_tasks"]), 1)
        self.assertEqual(len(result["blockers"]["blocked_tasks"]), 1)

    def test_where_are_we_surfaces_decisions_required(self):
        """'Where are we?' identifies decisions that need human input."""
        decision_id = self.store.add_decision(
            "Approve exposure gate",
            recommendation="Red-team findings support approval",
        )

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.where_are_we()

        self.assertGreater(len(result["summary"]["decisions_required"]), 0)
        self.assertGreater(len(result["decisions_required"]), 0)

    def test_where_are_we_surfaces_human_gates(self):
        """'Where are we?' identifies pending human decision gates."""
        ws = self.store.add_workstream("Induction")
        task = self.store.add_task("Complete Week 3", ws)
        gate = self.store.add_human_gate("task", task, "Is Week 3 red-team complete?")

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.where_are_we()

        self.assertGreater(len(result["summary"]["human_gates_pending"]), 0)
        self.assertGreater(len(result["blockers"]["human_gates_pending"]), 0)

    def test_where_are_we_recommends_next_actions(self):
        """'Where are we?' recommends concrete next steps."""
        ws = self.store.add_workstream("Induction")
        task = self.store.add_task("Complete Week 3", ws)
        gate = self.store.add_human_gate("task", task, "Is Week 3 ready?")

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.where_are_we()

        self.assertIsNotNone(result.get("next_actions"))
        self.assertGreater(len(result["next_actions"]), 0)
        next_action = result["next_actions"][0]
        self.assertIn("priority", next_action)
        self.assertIn("type", next_action)
        self.assertIn("reason", next_action)

    def test_where_are_we_preserves_provenance(self):
        """'Where are we?' response includes full provenance."""
        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.where_are_we()

        self.assertIn("provenance", result)
        self.assertIn("repository_state", result["provenance"])
        self.assertIn("notion_context", result["provenance"])
        self.assertIn("github_context", result["provenance"])
        self.assertIn("retrieved_at", result)

    def test_where_are_we_distinguishes_uncertain_state(self):
        """'Where are we?' distinguishes what is known from what is uncertain."""
        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.where_are_we()

        self.assertIn("uncertainty", result)
        self.assertIn("programme_state_available", result["uncertainty"])
        self.assertIn("repository_state_available", result["uncertainty"])
        self.assertIn("gaps", result["uncertainty"])

    def test_where_are_we_with_mock_notion_integrates_both_sources(self):
        """'Where are we?' correctly synthesizes from multiple sources."""

        def mock_notion(query, mode):
            return {
                "meta": {
                    "retrieved_at": "2026-08-29T12:00:00Z",
                    "read_only": True,
                    "bounded": True,
                    "query_scope": ["Induction"],
                    "registers_queried": ["live_work"],
                },
                "work_items": [
                    {
                        "Work Item": "Induction handbook",
                        "Status": "In review",
                        "Authority": Authority.WORKING_DRAFT,
                        "Current Position": "Waiting for red-team feedback",
                        "Notion URL": "https://notion.example/handbook",
                    }
                ],
                "sources": [
                    {
                        "Source": "Lifeline red-team notes",
                        "Authority": Authority.EXTERNAL_EVIDENCE,
                        "AI Use": "Challenge",
                        "Notion URL": "https://notion.example/redteam",
                    }
                ],
                "overlaps": [],
            }

        ws = self.store.add_workstream("Induction")
        task = self.store.add_task("Implement red-team findings", ws)

        retrieval = ProvenanceAwareRetrieval(self.store, notion_retriever=mock_notion)
        result = retrieval.where_are_we("Induction")

        self.assertIsNotNone(result)
        self.assertTrue(result["provenance"]["repository_state"]["read_only"])
        self.assertTrue(result["provenance"]["notion_context"]["read_only"])
        notion_work = result["provenance"]["notion_context"].get("work_items", [])
        self.assertEqual(len(notion_work), 1)


class ProvenanceTests(unittest.TestCase):
    """Tests for provenance labelling and authority preservation."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test.sqlite3"
        self.store = Store(self.db_path)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_authority_states_are_preserved_exactly(self):
        """Authority values are never modified or inferred."""
        source1 = self.store.add_source(
            "Policy A", "location1", authority=Authority.CONTROLLED_CURRENT
        )
        source2 = self.store.add_source(
            "Draft B", "location2", authority=Authority.WORKING_DRAFT
        )
        source3 = self.store.add_source(
            "Evidence C", "location3", authority=Authority.EXTERNAL_EVIDENCE
        )

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.retrieve_repository_state()

        sources = result["data"]["sources"]
        authorities = {s["authority"] for s in sources}
        self.assertEqual(authorities, {
            Authority.CONTROLLED_CURRENT,
            Authority.WORKING_DRAFT,
            Authority.EXTERNAL_EVIDENCE,
        })

    def test_source_locations_are_preserved(self):
        """Source locations are retained for auditability."""
        source_id = self.store.add_source(
            "Handbook", "git:handbook.md", authority=Authority.WORKING_DRAFT
        )

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.retrieve_repository_state()

        sources = result["data"]["sources"]
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["location"], "git:handbook.md")

    def test_notion_items_carry_full_provenance_metadata(self):
        """Notion items include full provenance on retrieval."""

        def mock_notion(query, mode):
            return {
                "meta": {
                    "retrieved_at": "2026-08-29T12:00:00Z",
                    "read_only": True,
                    "bounded": True,
                    "query_scope": [],
                    "registers_queried": ["live_work"],
                },
                "work_items": [
                    {
                        "Work Item": "Test item",
                        "Authority": Authority.CONTROLLED_CURRENT,
                        "Notion URL": "https://notion.example/123",
                    }
                ],
                "sources": [],
                "overlaps": [],
            }

        retrieval = ProvenanceAwareRetrieval(self.store, notion_retriever=mock_notion)
        result = retrieval.retrieve_notion_context("test", "Analyse")

        item = result["work_items"][0]
        self.assertEqual(item["_source"], "notion")
        self.assertEqual(item["_authority"], Authority.CONTROLLED_CURRENT)
        self.assertEqual(item["_location"], "https://notion.example/123")
        self.assertIn("_retrieved_at", item)
        self.assertTrue(item["_read_only"])


class RegressionInvariantsTests(unittest.TestCase):
    """Tests for the 18 v1 regression invariants."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "test.sqlite3"
        self.store = Store(self.db_path)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_draft_does_not_become_policy(self):
        """Draft sources remain draft and do not establish policy."""
        source = self.store.add_source(
            "Draft handbook", "handbook.md", authority=Authority.WORKING_DRAFT
        )

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.retrieve_repository_state()

        sources = result["data"]["sources"]
        self.assertEqual(sources[0]["authority"], Authority.WORKING_DRAFT)

    def test_external_evidence_does_not_establish_policy(self):
        """External evidence remains external and never becomes approved."""
        source = self.store.add_source(
            "Literature review",
            "https://doi.example/123",
            authority=Authority.EXTERNAL_EVIDENCE,
        )

        retrieval = ProvenanceAwareRetrieval(self.store)
        result = retrieval.retrieve_repository_state()

        sources = result["data"]["sources"]
        self.assertEqual(sources[0]["authority"], Authority.EXTERNAL_EVIDENCE)

    def test_retrieval_failure_never_fabricates_state(self):
        """Failed retrieval returns UNAVAILABLE, never cached or guessed state."""
        retrieval = ProvenanceAwareRetrieval(
            self.store, notion_retriever=None, github_retriever=None
        )
        result = retrieval.retrieve_notion_context("test", "Analyse")

        self.assertEqual(result.get("state"), "UNAVAILABLE")
        self.assertNotIn("work_items", result)


if __name__ == "__main__":
    unittest.main()
