"""Index repository metadata without treating files as approved programme policy."""
from pathlib import Path
from .store import Store

def index_markdown(root, store):
    root=Path(root); count=0
    for path in root.rglob("*.md"):
        if ".git" in path.parts or "__pycache__" in path.parts: continue
        relative=str(path.relative_to(root))
        authority="unclassified"
        if relative.startswith("specifications/"): authority="working draft"
        if relative in {"README.md","TAMMY.md"}: authority="controlled implementation brief"
        store.add_artefact(relative,"markdown file","located",authority)
        count+=1
    return count
