"""Small SQLite persistence layer with explicit provenance and human gates."""
import json, sqlite3, uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS workstreams (id TEXT PRIMARY KEY, name TEXT NOT NULL, status TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tasks (id TEXT PRIMARY KEY, title TEXT NOT NULL, status TEXT NOT NULL, priority TEXT NOT NULL DEFAULT 'normal', workstream_id TEXT, owner TEXT, blocked_by TEXT, human_decision_required INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY, name TEXT NOT NULL, location TEXT NOT NULL, authority TEXT NOT NULL DEFAULT 'unclassified', version TEXT, owner TEXT, status TEXT NOT NULL DEFAULT 'unknown', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS artefacts (id TEXT PRIMARY KEY, title TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'draft', authority TEXT NOT NULL DEFAULT 'unclassified', source_id TEXT, workstream_id TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS decisions (id TEXT PRIMARY KEY, question TEXT NOT NULL, status TEXT NOT NULL, recommendation TEXT, decision TEXT, rationale TEXT, source_ids_json TEXT NOT NULL DEFAULT '[]', human_decision_required INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS agents (id TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL, capabilities_json TEXT NOT NULL DEFAULT '[]', enabled INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS work_orders (id TEXT PRIMARY KEY, agent_id TEXT, task TEXT NOT NULL, deliverable TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'proposed', context_json TEXT NOT NULL DEFAULT '{}', human_decisions_reserved TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS human_gates (id TEXT PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, question TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'required', decision TEXT, decided_by TEXT, decided_at TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, event_type TEXT NOT NULL, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL);
"""
def now(): return datetime.now(timezone.utc).isoformat()
class Store:
    def __init__(self, path="data/tammy.sqlite3"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.db=sqlite3.connect(self.path,check_same_thread=False); self.db.row_factory=sqlite3.Row; self.db.executescript(SCHEMA); self.db.commit()
    def close(self): self.db.close()
    def _event(self, typ, entity, ident, payload): self.db.execute("INSERT INTO events VALUES (?,?,?,?,?,?)",(str(uuid.uuid4()),typ,entity,ident,json.dumps(payload),now()))
    def health(self): return {"ok":True,"storage":"sqlite","path":str(self.path),"schema":1}
    def list_state(self):
        tables=("workstreams","tasks","sources","artefacts","decisions","agents","work_orders","human_gates")
        order_by={"agents":"rowid","human_gates":"created_at"}
        return {t:[dict(r) for r in self.db.execute(f"SELECT * FROM {t} ORDER BY {order_by.get(t, 'updated_at')} DESC")] for t in tables}
    def add_workstream(self,name,description=""):
        ident,stamp=str(uuid.uuid4()),now(); self.db.execute("INSERT INTO workstreams VALUES (?,?,?,?,?,?)",(ident,name,"active",description,stamp,stamp)); self._event("created","workstream",ident,{"name":name}); self.db.commit(); return ident
    def add_task(self,title,workstream_id=None,priority="normal",human_decision_required=False):
        ident,stamp=str(uuid.uuid4()),now(); self.db.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?)",(ident,title,"open",priority,workstream_id,None,None,int(human_decision_required),stamp,stamp)); self._event("created","task",ident,{"title":title}); self.db.commit(); return ident
    def add_decision(self,question,recommendation=None,source_ids=()):
        ident,stamp=str(uuid.uuid4()),now(); self.db.execute("INSERT INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?)",(ident,question,"proposed",recommendation,None,None,json.dumps(list(source_ids)),1,stamp,stamp)); self._event("created","decision",ident,{"question":question}); self.db.commit(); return ident
    def add_source(self,name,location,authority="unclassified",version=None,owner=None):
        ident,stamp=str(uuid.uuid4()),now(); self.db.execute("INSERT INTO sources VALUES (?,?,?,?,?,?,?, ?,?)",(ident,name,location,authority,version,owner,"unknown",stamp,stamp)); self._event("created","source",ident,{"name":name,"authority":authority}); self.db.commit(); return ident
    def add_artefact(self,title,kind="file",status="located",authority="unclassified",source_id=None,workstream_id=None):
        ident,stamp=str(uuid.uuid4()),now(); self.db.execute("INSERT INTO artefacts VALUES (?,?,?,?,?,?,?,?,?)",(ident,title,kind,status,authority,source_id,workstream_id,stamp,stamp)); self._event("indexed","artefact",ident,{"title":title,"authority":authority}); self.db.commit(); return ident
    def add_agent(self,name,role,capabilities=()):
        ident=str(uuid.uuid4()); self.db.execute("INSERT INTO agents VALUES (?,?,?,?,?)",(ident,name,role,json.dumps(list(capabilities)),1)); self._event("created","agent",ident,{"name":name,"role":role}); self.db.commit(); return ident
    def add_work_order(self,agent_id,task,deliverable,context=None,human_decisions_reserved=""):
        ident,stamp=str(uuid.uuid4()),now(); self.db.execute("INSERT INTO work_orders VALUES (?,?,?,?,?,?,?,?,?)",(ident,agent_id,task,deliverable,"proposed",json.dumps(context or {}),human_decisions_reserved,stamp,stamp)); self._event("created","work_order",ident,{"agent_id":agent_id,"task":task}); self.db.commit(); return ident
    def add_human_gate(self,entity_type,entity_id,question):
        ident=str(uuid.uuid4()); self.db.execute("INSERT INTO human_gates VALUES (?,?,?,?,?,?,?,?,?)",(ident,entity_type,entity_id,question,"required",None,None,None,now())); self._event("created","human_gate",ident,{"question":question}); self.db.commit(); return ident
    def search(self, query):
        terms=[t for t in str(query or "").lower().split() if len(t)>2]
        if not terms: return {"tasks":[],"artefacts":[],"decisions":[],"sources":[]}
        def rows(table, fields):
            where=" OR ".join(f"lower({field}) LIKE ?" for field in fields); args=[f"%{term}%" for term in terms for _ in [0]]
            # Search each term against the concatenated searchable fields.
            clauses=[]; values=[]
            for term in terms: clauses.append("("+" OR ".join(f"lower({field}) LIKE ?" for field in fields)+")"); values.extend([f"%{term}%"]*len(fields))
            return [dict(r) for r in self.db.execute(f"SELECT * FROM {table} WHERE {' AND '.join(clauses)} ORDER BY rowid DESC LIMIT 20",values)]
        return {"tasks":rows("tasks",["title","status"]),"artefacts":rows("artefacts",["title","kind","authority"]),"decisions":rows("decisions",["question","recommendation","decision"]),"sources":rows("sources",["name","location","authority"])}
    def where_are_we(self, query=""):
        state=self.search(query) if query else self.list_state()
        tasks=state.get("tasks",[]); decisions=state.get("decisions",[]); orders=state.get("work_orders",[])
        return {"epistemic_status":"repository_state","query":query,"summary":{"active_workstreams":len(self.list_state()["workstreams"]),"open_tasks":sum(t.get("status") not in ("closed","complete") for t in tasks),"decisions_required":sum(d.get("human_decision_required") and d.get("status")!="decided" for d in decisions),"proposed_work_orders":sum(o.get("status")=="proposed" for o in orders)},"state":state,"human_decision_required":True,"provenance":"SQLite repository state; Notion programme state is not silently substituted."}
