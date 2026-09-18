"""Dependency-free HTTP API for the persistent Tammy state layer."""
import json, os
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .store import Store
from .indexer import index_markdown
STORE=Store(os.environ.get("TAMMY_STATE_DB","data/tammy.sqlite3"))
STATUS_PATH=Path(os.environ.get("TAMMY_STATUS_PATH",".tammy/status.json"))
QUEUE_PATH=Path(os.environ.get("TAMMY_QUEUE_PATH",".tammy/work-queue.json"))
class Handler(BaseHTTPRequestHandler):
    def send_json(self,code,body):
        raw=json.dumps(body,ensure_ascii=False).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/health": return self.send_json(200,STORE.health())
        if self.path=="/api/status":
            status=json.loads(STATUS_PATH.read_text()) if STATUS_PATH.exists() else {"state":"unknown"}
            queue=json.loads(QUEUE_PATH.read_text()) if QUEUE_PATH.exists() else {"items":[]}
            return self.send_json(200,{"status":status,"queue":queue.get("items",[]),"provenance":"repository .tammy status files"})
        if self.path=="/api/state": return self.send_json(200,STORE.list_state())
        if self.path.startswith("/api/where-are-we"):
            from urllib.parse import parse_qs, urlparse
            return self.send_json(200,STORE.where_are_we(parse_qs(urlparse(self.path).query).get("q",[""])[0]))
        self.send_json(404,{"error":"not found"})
    def do_POST(self):
        try: payload=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))) or b"{}")
        except Exception as exc: return self.send_json(400,{"error":str(exc)})
        if self.path=="/api/workstreams": return self.send_json(201,{"id":STORE.add_workstream(payload.get("name","Unnamed"),payload.get("description",""))})
        if self.path=="/api/tasks": return self.send_json(201,{"id":STORE.add_task(payload.get("title","Untitled"),payload.get("workstream_id"),payload.get("priority","normal"),payload.get("human_decision_required",False))})
        if self.path=="/api/decisions": return self.send_json(201,{"id":STORE.add_decision(payload.get("question","Decision required"),payload.get("recommendation"),payload.get("source_ids",[]))})
        if self.path=="/api/sources": return self.send_json(201,{"id":STORE.add_source(payload.get("name","Unnamed source"),payload.get("location","unknown"),payload.get("authority","unclassified"),payload.get("version"),payload.get("owner"))})
        if self.path=="/api/agents": return self.send_json(201,{"id":STORE.add_agent(payload.get("name","Unnamed agent"),payload.get("role","specialist"),payload.get("capabilities",[]))})
        if self.path=="/api/work-orders": return self.send_json(201,{"id":STORE.add_work_order(payload.get("agent_id"),payload.get("task","Bounded task"),payload.get("deliverable","Written result"),payload.get("context",{}),payload.get("human_decisions_reserved",""))})
        if self.path=="/api/human-gates": return self.send_json(201,{"id":STORE.add_human_gate(payload.get("entity_type","unknown"),payload.get("entity_id","unknown"),payload.get("question","Human decision required"))})
        if self.path=="/api/index": return self.send_json(200,{"indexed":index_markdown(payload.get("root","."),STORE)})
        self.send_json(404,{"error":"not found"})
    def log_message(self,*args): pass
def run(host="127.0.0.1",port=None):
    server=ThreadingHTTPServer((host,port or int(os.environ.get("TAMMY_STATE_PORT","3001"))),Handler); print(f"Tammy state backend listening on http://{host}:{server.server_port}"); server.serve_forever()
if __name__=="__main__": run()
