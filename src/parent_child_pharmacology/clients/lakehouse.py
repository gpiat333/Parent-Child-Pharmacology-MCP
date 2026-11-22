"""Lakehouse access: SQL warehouse (Statement Execution API) and Vector Search.
Auth is automatic inside Databricks Apps (the app's service principal)."""

import asyncio

from parent_child_pharmacology.core import config as cfg

_w = None
_audit_ready = False


def _client():
    global _w
    if _w is None:
        from databricks.sdk import WorkspaceClient  # lazy: keeps unit tests light

        _w = WorkspaceClient()
    return _w


def _sql(statement: str, params: dict | None = None) -> list[dict]:
    from databricks.sdk.service.sql import StatementParameterListItem

    r = _client().statement_execution.execute_statement(
        warehouse_id=cfg.WAREHOUSE_ID,
        statement=statement,
        wait_timeout="30s",
        parameters=[
            StatementParameterListItem(name=k, value=str(v)) for k, v in (params or {}).items()
        ],
    )
    if r.status.state.value != "SUCCEEDED":
        raise RuntimeError(r.status.error.message if r.status.error else r.status.state.value)
    if not r.manifest or not r.result or not r.result.data_array:
        return []
    cols = [c.name for c in r.manifest.schema.columns]
    return [dict(zip(cols, row)) for row in r.result.data_array]


def _vector(index_name: str, query: str, columns: list[str], k: int) -> list[dict]:
    r = _client().vector_search_indexes.query_index(
        index_name=index_name, columns=columns, query_text=query, num_results=k
    )
    if not r.result or not r.result.data_array:
        return []
    cols = [c.name for c in r.manifest.columns]
    return [dict(zip(cols, row)) for row in r.result.data_array]


async def sql(statement: str, params: dict | None = None) -> list[dict]:
    return await asyncio.to_thread(_sql, statement, params)


async def vector(index_name: str, query: str, columns: list[str], k: int = 5) -> list[dict]:
    return await asyncio.to_thread(_vector, index_name, query, columns, k)


async def log_call(tool: str, source: str, latency_ms: int, ok: bool, error: str | None) -> None:
    """Audit row. Deliberately stores NO user query text (medication questions can be sensitive)."""
    global _audit_ready
    if not _audit_ready:
        await sql(
            f"CREATE TABLE IF NOT EXISTS {cfg.table('mcp_audit_log')} "
            "(ts TIMESTAMP, tool STRING, source STRING, latency_ms BIGINT, ok BOOLEAN, error STRING)"
        )
        _audit_ready = True
    await sql(
        f"INSERT INTO {cfg.table('mcp_audit_log')} VALUES (current_timestamp(), :t, :s, :l, :o, :e)",
        {"t": tool, "s": source, "l": latency_ms, "o": str(ok).lower(), "e": error or ""},
    )
