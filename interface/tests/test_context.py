import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SERVER_PATH = Path(__file__).resolve().parents[1] / "server.py"
SPEC = importlib.util.spec_from_file_location("tammy_server", SERVER_PATH)
SERVER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SERVER
SPEC.loader.exec_module(SERVER)


def text_prop(prop_type, value):
    return {
        "type": prop_type,
        prop_type: [{"plain_text": value}],
    }


class ContextBoundaryTests(unittest.TestCase):
    def test_scopes_are_explicit_and_case_framework_is_not_any_case(self):
        self.assertEqual(SERVER.query_scopes("Compare the CARE Log and CRG"), ["CARE", "CRG"])
        self.assertEqual(SERVER.query_scopes("Review this case"), [])
        self.assertEqual(SERVER.query_scopes("Review the CASE framework"), ["PORF-CASE"])

    def test_live_work_filter_excludes_resolved_and_limits_scope(self):
        expected = {
            "and": [
                {"property": "Status", "select": {"does_not_equal": "Resolved"}},
                {"property": "Workstream", "multi_select": {"contains": "Induction"}},
            ]
        }
        self.assertEqual(SERVER.build_filter("live_work", ["Induction"]), expected)

    def test_projection_returns_only_allowlisted_metadata(self):
        page = {
            "url": "https://notion.example/work",
            "last_edited_time": "2026-08-27T12:00:00Z",
            "properties": {
                "Work Item": text_prop("title", "CARE Log"),
                "Current Position": text_prop("rich_text", "Working position"),
                "Status": {"type": "select", "select": {"name": "Progressing"}},
                "Secret Notes": text_prop("rich_text", "must not leave Notion"),
            },
        }
        projected = SERVER.project_page("live_work", page)
        self.assertEqual(projected["Work Item"], "CARE Log")
        self.assertEqual(projected["Status"], "Progressing")
        self.assertNotIn("Secret Notes", projected)

    @patch.object(SERVER, "notion_request")
    def test_query_projection_resolves_only_allowlisted_property_ids(self, notion_request):
        SERVER.PROPERTY_ID_CACHE.clear()
        notion_request.return_value = {
            "properties": {
                name: {"id": f"id-{index}"}
                for index, name in enumerate(SERVER.FIELD_PROJECTIONS["live_work"])
            }
        }
        ids = SERVER.filter_property_ids("live_work")
        self.assertEqual(len(ids), len(SERVER.FIELD_PROJECTIONS["live_work"]))
        self.assertNotIn("AI Contribution", SERVER.FIELD_PROJECTIONS["live_work"])
        notion_request.assert_called_once_with(
            f"/data_sources/{SERVER.DATA_SOURCES['live_work']}", method="GET"
        )

    @patch.object(SERVER, "query_data_source")
    def test_generic_opening_retrieval_reads_only_live_work(self, query_data_source):
        query_data_source.return_value = []
        context = SERVER.retrieve_context("current active programme work", "Analyse")
        self.assertEqual(query_data_source.call_args_list[0].args, ("live_work", []))
        self.assertEqual(query_data_source.call_count, 1)
        self.assertEqual(context["meta"]["registers_queried"], ["live_work"])
        self.assertFalse(context["meta"]["full_page_content_retrieved"])

    @patch.object(SERVER, "query_data_source")
    def test_compare_retrieval_is_bounded_to_relevant_registers(self, query_data_source):
        query_data_source.return_value = []
        context = SERVER.retrieve_context("Compare CARE Log evidence and secondary assessment", "Compare")
        calls = [call.args[0] for call in query_data_source.call_args_list]
        self.assertEqual(calls, ["live_work", "sources", "overlaps"])
        self.assertEqual(context["meta"]["query_scope"], ["CARE"])
        self.assertTrue(context["meta"]["read_only"])
        self.assertEqual(context["meta"]["limits"], {"live_work": 8, "sources": 6, "overlaps": 5})

    def test_missing_token_fails_closed(self):
        with patch.object(SERVER, "NOTION_TOKEN", None):
            with self.assertRaises(SERVER.NotionUnavailable) as caught:
                SERVER.notion_request("/data_sources/example/query", {})
        self.assertIn("not configured", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
