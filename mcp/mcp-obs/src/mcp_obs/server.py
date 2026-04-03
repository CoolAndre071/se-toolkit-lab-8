"""Stdio MCP server exposing VictoriaLogs and VictoriaTraces as typed tools."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

from mcp_obs.settings import resolve_settings


class LogSearchArgs(BaseModel):
    query: str = Field(
        description="LogsQL query, e.g. '_time:10m severity:ERROR service.name:\"Learning Management Service\"'"
    )
    limit: int = Field(default=20, ge=1, le=100, description="Max log entries to return")


class LogErrorCountArgs(BaseModel):
    minutes: int = Field(default=60, ge=1, le=1440, description="Time window in minutes")
    service: str = Field(
        default="Learning Management Service",
        description="Service name to count errors for",
    )


class TracesListArgs(BaseModel):
    service: str = Field(
        default="Learning Management Service",
        description="Service name to list traces for",
    )
    limit: int = Field(default=10, ge=1, le=50, description="Max traces to return")


class TracesGetArgs(BaseModel):
    trace_id: str = Field(description="Trace ID to fetch, e.g. '541a62dc1884f22175ee16702ace399e'")


async def _logs_search(client: httpx.AsyncClient, vl_base: str, args: LogSearchArgs) -> str:
    """Search VictoriaLogs using LogsQL."""
    resp = await client.post(
        f"{vl_base}/select/logsql/query",
        params={"query": args.query, "limit": args.limit},
        timeout=15,
    )
    resp.raise_for_status()
    entries = []
    for line in resp.text.strip().splitlines():
        if line.strip():
            entries.append(json.loads(line))
    if not entries:
        return f"No log entries found for query: {args.query}"
    result_lines = [f"Found {len(entries)} log entries for query: {args.query}\n"]
    for e in entries:
        ts = e.get("_time", "?")
        sev = e.get("severity", "?")
        svc = e.get("service.name", "?")
        msg = e.get("_msg", "")
        trace_id = e.get("otelTraceID", "") or e.get("trace_id", "")
        event = e.get("event", "")
        line = f"[{ts}] {sev} {svc}"
        if event:
            line += f" event={event}"
        if trace_id:
            line += f" trace_id={trace_id}"
        line += f" | {msg}"
        result_lines.append(line)
    return "\n".join(result_lines)


async def _logs_error_count(client: httpx.AsyncClient, vl_base: str, args: LogErrorCountArgs) -> str:
    """Count errors in VictoriaLogs over a time window."""
    query = f'_time:{args.minutes}m severity:ERROR service.name:"{args.service}"'
    resp = await client.post(
        f"{vl_base}/select/logsql/query",
        params={"query": query, "limit": 1000},
        timeout=15,
    )
    resp.raise_for_status()
    count = 0
    recent: list[dict] = []
    for line in resp.text.strip().splitlines():
        if line.strip():
            entry = json.loads(line)
            count += 1
            if len(recent) < 5:
                recent.append(entry)
    if count == 0:
        return f"No ERROR entries found for {args.service} in the last {args.minutes} minutes."
    lines = [f"Found {count} ERROR entries for '{args.service}' in the last {args.minutes} minutes.\n"]
    lines.append("Most recent errors:")
    for e in recent:
        ts = e.get("_time", "?")
        msg = e.get("_msg", "")
        event = e.get("event", "")
        trace_id = e.get("otelTraceID", "") or e.get("trace_id", "")
        line = f"  [{ts}] event={event}"
        if trace_id:
            line += f" trace_id={trace_id}"
        line += f" | {msg}"
        lines.append(line)
    return "\n".join(lines)


async def _traces_list(client: httpx.AsyncClient, vt_base: str, args: TracesListArgs) -> str:
    """List recent traces from VictoriaTraces (Jaeger-compatible API)."""
    resp = await client.get(
        f"{vt_base}/select/jaeger/api/traces",
        params={"service": args.service, "limit": args.limit},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    traces = data.get("data", [])
    if not traces:
        return f"No traces found for service '{args.service}'."
    lines = [f"Found {len(traces)} recent traces for '{args.service}':\n"]
    for t in traces:
        tid = t.get("traceID", "?")
        spans = t.get("spans", [])
        services = sorted(set(s.get("process", {}).get("serviceName", "?") for s in spans))
        # Find root spans to get operation name
        root_ops = []
        for s in spans:
            if not s.get("references"):
                root_ops.append(s.get("operationName", "?"))
        op = root_ops[0] if root_ops else (spans[0].get("operationName", "?") if spans else "?")
        # Duration
        durations = [s.get("duration", 0) for s in spans]
        max_dur = max(durations) if durations else 0
        lines.append(f"  trace_id={tid} op={op} services={', '.join(services)} max_duration={max_dur/1000:.0f}ms")
    return "\n".join(lines)


async def _traces_get(client: httpx.AsyncClient, vt_base: str, args: TracesGetArgs) -> str:
    """Fetch a specific trace by ID from VictoriaTraces."""
    resp = await client.get(
        f"{vt_base}/select/jaeger/api/traces/{args.trace_id}",
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    traces = data.get("data", [])
    if not traces:
        return f"No trace found with ID '{args.trace_id}'."
    t = traces[0]
    spans = t.get("spans", [])
    # Build span hierarchy
    span_map = {s["spanID"]: s for s in spans}
    lines = [f"Trace {args.trace_id} ({len(spans)} spans):\n"]
    for s in sorted(spans, key=lambda x: x.get("startTime", 0)):
        # Calculate depth
        depth = 0
        refs = s.get("references", [])
        pid = refs[0]["spanID"] if refs else None
        visited = set()
        while pid and pid not in visited:
            depth += 1
            visited.add(pid)
            p = span_map.get(pid)
            if p:
                refs = p.get("references", [])
                pid = refs[0]["spanID"] if refs else None
            else:
                break
        op = s.get("operationName", "?")
        dur = s.get("duration", 0)
        tags = {tg["key"]: tg["value"] for tg in s.get("tags", []) if "key" in tg}
        status = tags.get("http.status_code", "")
        error = tags.get("error", False)
        indent = "  " * depth
        status_str = f" HTTP {status}" if status else ""
        error_str = " [ERROR]" if error else ""
        lines.append(f"{indent}├─ {op}{status_str}{error_str} ({dur/1000:.0f}ms)")
    return "\n".join(lines)


def create_server(vl_base: str, vt_base: str) -> Server:
    server = Server("obs")

    tool_specs = [
        ("obs_logs_search", "Search structured logs in VictoriaLogs using LogsQL. Use to find errors, events, or specific requests.", LogSearchArgs),
        ("obs_logs_error_count", "Count ERROR level log entries for a service over a time window. Use first when asked about errors.", LogErrorCountArgs),
        ("obs_traces_list", "List recent traces (traces) for a service from VictoriaTraces. Returns trace IDs, operations, and durations.", TracesListArgs),
        ("obs_traces_get", "Fetch a specific trace by ID to inspect the full span hierarchy. Use after finding a trace_id from logs or traces_list.", TracesGetArgs),
    ]

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [Tool(name=name, description=desc, inputSchema=model.model_json_schema()) for name, desc, model in tool_specs]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
        args = arguments or {}
        async with httpx.AsyncClient() as client:
            try:
                if name == "obs_logs_search":
                    result = await _logs_search(client, vl_base, LogSearchArgs(**args))
                elif name == "obs_logs_error_count":
                    result = await _logs_error_count(client, vl_base, LogErrorCountArgs(**args))
                elif name == "obs_traces_list":
                    result = await _traces_list(client, vt_base, TracesListArgs(**args))
                elif name == "obs_traces_get":
                    result = await _traces_get(client, vt_base, TracesGetArgs(**args))
                else:
                    result = f"Unknown tool: {name}"
            except Exception as exc:
                result = f"Error: {type(exc).__name__}: {exc}"
        return [TextContent(type="text", text=result)]

    _ = list_tools, call_tool
    return server


async def main() -> None:
    settings = resolve_settings()
    server = create_server(settings.victorialogs_url, settings.victoriatraces_url)
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
