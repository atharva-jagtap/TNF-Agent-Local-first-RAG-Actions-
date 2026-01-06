import os, sqlite3, re
from typing import Dict, Any

DB_PATH = os.path.abspath("data/tnf/tnf.db")

class SQLTool:
    @staticmethod
    def describe():
        return ("Tool: sql\n"
                "Usage: start your message with 'sql:' followed by a single SELECT query. "
                f"DB: {DB_PATH} (read-only).")

    @staticmethod
    def should_run(text: str) -> bool:
        return text.strip().lower().startswith("sql:")

    @staticmethod
    def run(text: str) -> str:
        q = text.split(":",1)[1].strip()
        if not re.match(r"^\s*select\b", q, re.IGNORECASE):
            return "Only SELECT statements are allowed."
        uri = f"file:{DB_PATH}?mode=ro"
        try:
            with sqlite3.connect(uri, uri=True) as conn:
                cur = conn.execute(q)
                cols = [c[0] for c in cur.description]
                rows = cur.fetchmany(50)
                out = [", ".join(cols)]
                for r in rows:
                    out.append(", ".join(str(x) for x in r))
                if len(rows) == 0:
                    return "(no rows)"
                return "\n".join(out)
        except Exception as e:
            return f"SQL error: {e}"

TOOL_REGISTRY: Dict[str, Any] = {"sql": SQLTool}
