import tempfile, unittest
from pathlib import Path
from backend.store import Store
from backend.indexer import index_markdown

class StoreTests(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.path=Path(self.tmp.name)/"state.sqlite3"; self.store=Store(self.path)
    def tearDown(self): self.store.close(); self.tmp.cleanup()
    def test_state_is_persistent_and_types_are_distinct(self):
        ws=self.store.add_workstream("Induction"); task=self.store.add_task("Review Week 3",ws,human_decision_required=True); decision=self.store.add_decision("Approve exposure gate", "Red-team first")
        self.store.close(); reopened=Store(self.path); state=reopened.list_state()
        self.assertEqual(len(state["workstreams"]),1); self.assertEqual(state["tasks"][0]["id"],task); self.assertEqual(state["tasks"][0]["human_decision_required"],1); self.assertEqual(state["decisions"][0]["id"],decision); self.assertNotEqual(task,decision); reopened.close()
    def test_health_does_not_expose_credentials(self): self.assertTrue(self.store.health()["ok"]); self.assertNotIn("TOKEN",str(self.store.health()))
    def test_indexer_preserves_unknown_authority_and_marks_specs_as_drafts(self):
        root=Path(self.tmp.name)/"repo"; (root/"specifications").mkdir(parents=True); (root/"specifications"/"gate.md").write_text("draft",encoding="utf-8"); (root/"notes.md").write_text("note",encoding="utf-8")
        self.assertEqual(index_markdown(root,self.store),2)
        rows=self.store.list_state()["artefacts"]
        self.assertEqual({r["authority"] for r in rows},{"working draft","unclassified"})
    def test_provenance_agents_and_human_gate_are_persisted(self):
        source=self.store.add_source("Induction handbook","git:handbook.md","working draft","0.1")
        agent=self.store.add_agent("Claude","red-team",["challenge","curriculum"])
        order=self.store.add_work_order(agent,"Review Week 3","Red-team report",{"source_id":source},"Exposure gate approval")
        gate=self.store.add_human_gate("work_order",order,"Accept the recommendation?")
        state=self.store.list_state()
        self.assertEqual(state["sources"][0]["authority"],"working draft")
        self.assertEqual(state["work_orders"][0]["status"],"proposed")
        self.assertEqual(state["human_gates"][0]["status"],"required")
