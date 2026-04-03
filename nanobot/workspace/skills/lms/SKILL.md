---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

Use the LMS MCP tools to answer questions about courses, labs, learners, and performance data. Always call the actual tools — never guess or rely on cached knowledge.

## Available tools

| Tool | When to use |
|------|-------------|
| `lms_health` | Check if the LMS backend is reachable and get the total item count |
| `lms_labs` | List all available labs — call this first when the user asks about labs, scores, pass rates, or anything lab-related without naming a specific lab |
| `lms_learners` | List all registered learners |
| `lms_pass_rates` | Get per-task average scores and attempt counts for a **specific lab** (requires `lab` parameter) |
| `lms_timeline` | Get submission timeline (date + submission count) for a **specific lab** |
| `lms_groups` | Get group performance (average score + student count per group) for a **specific lab** |
| `lms_top_learners` | Get top learners by average score for a **specific lab** (optional `limit`, default 5) |
| `lms_completion_rate` | Get overall completion rate (passed / total) for a **specific lab** |
| `lms_sync_pipeline` | Trigger the LMS sync pipeline when data seems stale or missing |

## Strategy

- **If the user asks about labs, scores, pass rates, completion, groups, timeline, or top learners without naming a lab:** call `lms_labs` first to discover what's available.
- **If a lab parameter is needed and not provided:** use `lms_labs` to find available labs, then ask the user which one they want.
- **If multiple labs are available:** present the lab list and ask the user to choose one. Use the lab title from the `lms_labs` output as the user-facing label unless the tool output provides a better identifier.
- **For "what can you do?" questions:** explain that you can query the LMS for lab listings, pass rates, completion rates, learner rankings, group performance, submission timelines, and overall system health. Mention that you need a specific lab name for most detailed queries.
- **Format numeric results clearly:** use tables or bullet points for percentages, counts, and rankings. Keep responses concise.
- **If the backend reports healthy but shows no data:** suggest calling `lms_sync_pipeline` to refresh the data, then retry the original query.
- **Let the shared `structured-ui` skill decide how to present choices on supported channels** — don't duplicate choice-rendering logic here.
