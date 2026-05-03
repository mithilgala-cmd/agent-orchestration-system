from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from sandbox import sandbox

# ── Web Search ────────────────────────────────────────────────────────────────
_ddg = DuckDuckGoSearchRun()

@tool
def web_search_tool(query: str) -> str:
    """Search the web for up-to-date information on a topic."""
    try:
        return _ddg.run(query)
    except Exception as e:
        return f"Search failed: {e}"


# ── Python Code Execution (Docker sandbox) ────────────────────────────────────
@tool
def execute_python_tool(code: str) -> str:
    """
    Execute Python code in a sandboxed Docker container and return stdout/stderr.
    Use this to run calculations, data processing, or generate scripts.
    """
    result = sandbox.execute_code(code)
    if result["status"] == "error":
        return f"ERROR: {result['output']}"
    return result["output"] or "(no output)"


# ── File Writer ───────────────────────────────────────────────────────────────
@tool
def write_file_tool(file_path: str, content: str) -> str:
    """Write text content to a local file. Creates parent directories if needed."""
    import os
    try:
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} chars to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"
