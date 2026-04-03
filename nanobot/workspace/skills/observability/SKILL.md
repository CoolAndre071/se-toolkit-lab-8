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
- **When the user asks "What went wrong?" or "Check system health":** perform a full investigation in one pass:
  1. Call `obs_logs_error_count` with a narrow window (last 10 minutes) for the LMS backend.
  2. If errors exist, call `obs_logs_search` with a scoped query to get the most recent error entries — look for `event`, `trace_id`, HTTP status codes, and error messages.
  3. Extract the most relevant `trace_id` from the log entries and call `obs_traces_get` to fetch the full trace. Examine the span hierarchy to find exactly which operation failed.
  4. Write a concise summary that mentions: (a) the log evidence — what errors were found and when, (b) the trace evidence — which service and operation failed, (c) your conclusion about the root cause. Do NOT dump raw JSON or list every log entry.
  5. If there is a discrepancy between the log/trace evidence and the HTTP status the backend reports (e.g., logs show a database failure but the backend returns 404), call that out explicitly — it suggests a bug in the backend's error-handling path.
