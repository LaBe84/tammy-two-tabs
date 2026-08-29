#!/usr/bin/env python3
"""Local Tammy v2 bridge with bounded, read-only Notion retrieval."""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = int(os.environ.get("TAMMY_V2_PORT", "4173"))
BACKEND_URL = os.environ.get("TAMMY_BACKEND_URL", "http://127.0.0.1:3000/api/tammy")
STATE_BACKEND_URL = os.environ.get("TAMMY_STATE_BACKEND_URL", "http://127.0.0.1:3001")
ROOT = Path(__file__).resolve().parent

NOTION_API_BASE = os.environ.get("TAMMY_NOTION_API_BASE", "https://api.notion.com/v1").rstrip("/")
NOTION_VERSION = os.environ.get("TAMMY_NOTION_VERSION", "2026-03-11")
NOTION_TOKEN = (
    os.environ.get("TAMMY_NOTION_TOKEN")
    or os.environ.get("NOTION_TOKEN")
    or os.environ.get("NOTION_API_KEY")
    or os.environ.get("NOTION_INTEGRATION_TOKEN")
)

DATA_SOURCES = {
    "live_work": os.environ.get(
        "TAMMY_NOTION_LIVE_WORK_ID", "597c5d99-94cc-4fa6-b8d5-b6b9a69b1dc5"
    ),
    "sources": os.environ.get(
        "TAMMY_NOTION_SOURCE_REGISTER_ID", "eb2afad3-91ae-4b84-b7a7-3e662f681a97"
    ),
    "overlaps": os.environ.get(
        "TAMMY_NOTION_OVERLAP_MAP_ID", "73d0fb9f-1675-48f4-832b-21a2e3547dc1"
    ),
}

FIELD_PROJECTIONS = {
    "live_work": [
        "Work Item", "Workstream", "Status", "Authority", "Current Position",
        "Decision Needed", "Next Action", "Evidence Strength", "Overlap Key",
        "Merge State", "Last Reviewed", "Owner",
    ],
    "sources": [
        "Source", "Domain", "Authority", "Version", "Owner", "Authority Note",
        "AI Use", "Source URL", "Last Checked", "Effective Date", "Review Date",
    ],
    "overlaps": [
        "Overlap", "Overlap Key", "Primary Workstream", "Related Workstreams",
        "Shared Issue", "Existing Position", "State", "Human Decision",
        "Last Reviewed", "Sources",
    ],
}

QUERY_LIMITS = {"live_work": 8, "sources": 6, "overlaps": 5}
PROPERTY_ID_CACHE = {}

WORKSTREAM_ALIASES = {
    "CARE": ("care log", "care-log", "secondary assessment", "care assessment"),
    "CRG": ("crg", "clinical review group"),
    "Induction": ("induction", "induction handbook", "learning programme", "training resource"),
    "ERO": ("ero", "emergency response", "right care right person", "rcrp"),
    "SAI": ("sai", "serious adverse incident", "patient a", "level 1 review", "level 2 review"),
    "PORF-CASE": ("porf", "case framework", "case enquiry", "suicide enquiry"),
    "SMHS": ("smhs", "student mental health"),
    "Lifeline": ("lifeline", "helpline", "community counselling", "community counseling"),
}

SOURCE_TERMS = {
    "source", "evidence", "document", "policy", "guidance", "authority",
    "approved", "controlled", "current version", "citation",
}

OVERLAP_TERMS = {
    "overlap", "conflict", "contradiction", "duplicate", "same issue",
    "compare", "merge", "link",
}


class NotionUnavailable(RuntimeError):
    """Raised when bounded Notion retrieval cannot complete safely."""


def compact_text(value, limit=700):
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def query_scopes(query):
    haystack = f" {str(query or '').lower()} "
    scopes = []
    for workstream, aliases in WORKSTREAM_ALIASES.items():
        if any(alias in haystack for alias in aliases):
            scopes.append(workstream)
    return scopes


def mentions_any(query, terms):
    haystack = str(query or "").lower()
    return any(term in haystack for term in terms)


def property_filter(property_name, property_type, operator, value):
    return {"property": property_name, property_type: {operator: value}}


def combine_filters(base_filter, scope_filters):
    if not scope_filters:
        return base_filter
    scoped = scope_filters[0] if len(scope_filters) == 1 else {"or": scope_filters}
    return {"and": [base_filter, scoped]}


def build_filter(register, scopes):
    if register == "live_work":
        base = property_filter("Status", "select", "does_not_equal", "Resolved")
        scoped = [
            property_filter("Workstream", "multi_select", "contains", scope)
            for scope in scopes
        ]
        return combine_filters(base, scoped)

    if register == "sources":
        base = property_filter("Authority", "select", "does_not_equal", "Archived")
        scoped = [
            property_filter("Domain", "multi_select", "contains", scope)
            for scope in scopes
        ]
        return combine_filters(base, scoped)

    base = property_filter("State", "select", "does_not_equal", "Merged")
    scoped = []
    for scope in scopes:
        if scope == "Lifeline":
            continue
        scoped.extend([
            property_filter("Primary Workstream", "select", "equals", scope),
            property_filter("Related Workstreams", "multi_select", "contains", scope),
        ])
    return combine_filters(base, scoped)


def notion_request(path, body=None, method="POST"):
    if not NOTION_TOKEN:
        raise NotionUnavailable(
            "Notion token is not configured. Set TAMMY_NOTION_TOKEN, NOTION_TOKEN, "
            "NOTION_API_KEY or NOTION_INTEGRATION_TOKEN before starting the bridge."
        )

    request = urllib.request.Request(
        f"{NOTION_API_BASE}{path}",
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
            "User-Agent": "Tammy-Two-Tabs/2",
        },
        method=method,
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 529) and attempt < 2:
                retry_after = min(float(exc.headers.get("Retry-After", "1")), 5.0)
                time.sleep(max(retry_after, 0.25) * (attempt + 1))
                continue
            detail = ""
            try:
                payload = json.loads(exc.read().decode("utf-8"))
                detail = payload.get("message") or payload.get("code") or ""
            except Exception:
                pass
            message = f"Notion returned HTTP {exc.code}"
            if detail:
                message += f": {detail}"
            raise NotionUnavailable(message) from exc
        except Exception as exc:
            raise NotionUnavailable(f"Notion retrieval failed: {exc}") from exc

    raise NotionUnavailable("Notion retrieval failed after bounded retries.")


def filter_property_ids(register):
    if register in PROPERTY_ID_CACHE:
        return PROPERTY_ID_CACHE[register]

    schema = notion_request(f"/data_sources/{DATA_SOURCES[register]}", method="GET")
    properties = schema.get("properties", {})
    missing = [name for name in FIELD_PROJECTIONS[register] if name not in properties]
    if missing:
        raise NotionUnavailable(
            f"Notion {register} schema is missing required properties: {', '.join(missing)}"
        )
    property_ids = [properties[name].get("id") for name in FIELD_PROJECTIONS[register]]
    if any(not property_id for property_id in property_ids):
        raise NotionUnavailable(f"Notion {register} schema returned an empty property id.")
    PROPERTY_ID_CACHE[register] = property_ids
    return property_ids


def query_data_source(register, scopes):
    body = {
        "page_size": QUERY_LIMITS[register],
        "filter": build_filter(register, scopes),
    }
    sort_property = {
        "live_work": "Last Reviewed",
        "sources": "Last Checked",
        "overlaps": "Last Reviewed",
    }[register]
    body["sorts"] = [{"property": sort_property, "direction": "descending"}]
    params = urllib.parse.urlencode(
        [("filter_properties[]", property_id) for property_id in filter_property_ids(register)]
    )
    response = notion_request(
        f"/data_sources/{DATA_SOURCES[register]}/query?{params}", body
    )
    return response.get("results", [])[: QUERY_LIMITS[register]]


def rich_text_value(parts):
    return "".join(part.get("plain_text", "") for part in (parts or []))


def property_value(prop):
    if not isinstance(prop, dict):
        return None
    prop_type = prop.get("type")
    if prop_type in ("title", "rich_text"):
        return compact_text(rich_text_value(prop.get(prop_type, [])))
    if prop_type in ("select", "status"):
        item = prop.get(prop_type)
        return item.get("name") if item else None
    if prop_type == "multi_select":
        return [item.get("name") for item in prop.get("multi_select", []) if item.get("name")]
    if prop_type == "date":
        item = prop.get("date")
        return item.get("start") if item else None
    if prop_type == "url":
        return prop.get("url")
    if prop_type == "number":
        return prop.get("number")
    if prop_type == "unique_id":
        item = prop.get("unique_id") or {}
        number = item.get("number")
        return f"{item.get('prefix') or ''}{number}" if number is not None else None
    if prop_type == "checkbox":
        return bool(prop.get("checkbox"))
    return None


def project_page(register, page):
    properties = page.get("properties", {})
    projected = {
        field: property_value(properties.get(field))
        for field in FIELD_PROJECTIONS[register]
    }
    projected = {key: value for key, value in projected.items() if value not in (None, "", [])}
    projected["Notion URL"] = page.get("url")
    projected["Last edited"] = page.get("last_edited_time")
    return projected


def retrieve_context(query, mode="Analyse"):
    query = compact_text(query, 1200)
    mode = compact_text(mode, 40) or "Analyse"
    scopes = query_scopes(query)
    lower_mode = mode.lower()
    include_sources = bool(scopes) and (
        lower_mode == "compare" or mentions_any(query, SOURCE_TERMS)
    )
    include_overlaps = (
        bool(scopes)
        or lower_mode in ("compare", "challenge", "decide")
        or mentions_any(query, OVERLAP_TERMS)
    )

    registers_queried = ["live_work"]
    raw = {"live_work": query_data_source("live_work", scopes), "sources": [], "overlaps": []}
    if include_sources:
        raw["sources"] = query_data_source("sources", scopes)
        registers_queried.append("sources")
    if include_overlaps:
        raw["overlaps"] = query_data_source("overlaps", scopes)
        registers_queried.append("overlaps")

    return {
        "meta": {
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "read_only": True,
            "bounded": True,
            "notion_version": NOTION_VERSION,
            "query_scope": scopes or ["active non-resolved work"],
            "registers_queried": registers_queried,
            "limits": {name: QUERY_LIMITS[name] for name in registers_queried},
            "properties_requested": {
                name: FIELD_PROJECTIONS[name] for name in registers_queried
            },
            "full_page_content_retrieved": False,
        },
        "work_items": [project_page("live_work", page) for page in raw["live_work"]],
        "sources": [project_page("sources", page) for page in raw["sources"]],
        "overlaps": [project_page("overlaps", page) for page in raw["overlaps"]],
    }


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        original = super().translate_path(path)
        rel = os.path.relpath(original, os.getcwd())
        return str(ROOT / rel)

    def send_json(self, status, payload):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 65536:
            raise ValueError("Request body exceeds 64 KiB.")
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        if self.path == "/api/state" or self.path.startswith("/api/where-are-we") or self.path == "/api/status":
            target = f"{STATE_BACKEND_URL}{self.path}"
            try:
                with urllib.request.urlopen(target, timeout=10) as upstream:
                    data = upstream.read(); self.send_response(upstream.status); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            except Exception as exc:
                self.send_json(503, {"error": f"Tammy state backend unavailable at {STATE_BACKEND_URL}: {exc}", "state": "UNAVAILABLE"})
            return
        if self.path == "/api/context/health":
            self.send_json(200, {
                "configured": bool(NOTION_TOKEN),
                "read_only": True,
                "notion_version": NOTION_VERSION,
                "register_count": 3,
            })
            return
        super().do_GET()

    def do_POST(self):
        if self.path == "/api/context":
            try:
                payload = self.read_json()
                context = retrieve_context(payload.get("query", ""), payload.get("mode", "Analyse"))
                self.send_json(200, context)
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(400, {"error": str(exc)})
            except NotionUnavailable as exc:
                self.send_json(503, {
                    "error": str(exc),
                    "programme_context": "UNAVAILABLE",
                    "read_only": True,
                })
            return

        if self.path != "/api/tammy":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length)
        request = urllib.request.Request(
            BACKEND_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as upstream:
                data = upstream.read()
                self.send_response(upstream.status)
                self.send_header("Content-Type", upstream.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as exc:
            data = exc.read() or json.dumps({"error": f"Tammy backend returned {exc.code}"}).encode()
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as exc:
            self.send_json(502, {"error": f"Could not reach Tammy backend at {BACKEND_URL}: {exc}"})


if __name__ == "__main__":
    os.chdir(ROOT)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Tammy v2 interface: http://localhost:{PORT}")
    print(f"Proxying live Tammy requests to: {BACKEND_URL}")
    print("Notion context: " + (
        f"configured, read-only ({NOTION_VERSION})" if NOTION_TOKEN else "not configured"
    ))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Tammy v2.")
