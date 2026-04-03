---
name: observability
description: Use observability MCP tools to search logs and traces for errors and system health
always: true
---

# Observability Skill

Use the observability MCP tools (`obs_logs_search`, `obs_logs_error_count`, `obs_traces_list`, `obs_traces_get`) to answer questions about system health, errors, and failures.

## Strategy

- **When the user asks about errors or system health:** start with `obs_logs_error_count` to quickly check if there are recent errors for the LMS backend. Use a narrow time window (e.g., 10 minutes) to avoid surfacing unrelated older errors.
- **If errors are found:** use `obs_logs_search` to inspect the most recent error entries. Look for `event`, `trace_id`, and error messages. Extract relevant `trace_id` values.
- **If a trace_id is found:** use `obs_traces_get` to fetch the full trace and inspect the span hierarchy. Identify which service and operation failed.
- **To list recent traces:** use `obs_traces_list` when the user wants to see what requests have been processed recently.
- **Summarize findings concisely.** Don't dump raw JSON. Present a short summary: what happened, when, which service, and whether there's a trace to investigate further.
- **Scope queries to the LMS backend.** The user usually cares about "Learning Management Service" errors, not errors from other services like Qwen Code API. Use `service.name:"Learning Management Service"` in LogsQL queries.
- **If the user asks a broad question like "any errors in the last hour?":** narrow it to `service.name:"Learning Management Service"` and `_time:10m` by default, unless they specify a different window or service.
