# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

### "What is the agentic loop?"

The agent explains the perceive → reason → act → observe cycle that distinguishes
an AI agent from a simple chatbot. An agent loops through autonomous steps until
the goal is achieved, rather than giving a one-shot response.

### "What labs are available in our LMS?" (without MCP tools)

Without MCP tools configured, the agent inspects local repo files (README.md, task
markdown files) and answers from documentation. It lists the lab titles it finds
in the repository but **cannot** return live data from the backend. It may list
"lab-08" or other entries it discovered by reading local files rather than querying
the running API.

> Note: The first run of `cli:task1a-labs` showed the agent reading local repo
> documentation (README.md, task files) and listing lab titles from there — not from
> the live backend.

## Task 1B — Agent with LMS tools

### "What labs are available?" (with MCP tools)

With the LMS MCP server configured, the agent calls `lms_labs` and returns real
lab names from the backend:

| # | Lab |
|---|-----|
| 1 | Lab 01 – Products, Architecture & Roles |
| 2 | Lab 02 — Run, Fix, and Deploy a Backend Service |
| 3 | Lab 03 — Backend API: Explore, Debug, Implement, Deploy |
| 4 | Lab 04 — Testing, Front-end, and AI Agents |
| 5 | Lab 05 — Data Pipeline and Analytics Dashboard |
| 6 | Lab 06 — Build Your Own Agent |
| 7 | Lab 07 — Build a Client with an AI Coding Agent |
| 8 | lab-08 |

### "Is the LMS backend healthy?"

The agent calls `lms_health` and reports: "Yes, the LMS backend is healthy! It
currently has 56 items."

### "Which lab has the lowest pass rate?"

The agent chains multiple tool calls: first `lms_labs` to discover all labs, then
`lms_completion_rate` for each lab in parallel. It reports that only Lab 01 has
submission data (93.9% completion rate, 108/115 students passed), while labs 02–08
show 0 submissions.

## Task 1C — Skill prompt

### "Show me the scores" (without specifying a lab)

With the LMS skill loaded, the agent calls `lms_labs` first, then fetches completion
rates and group performance for all labs that have data. It presents:

- **Lab Completion Rates** — Lab 01: 93.9% (108/115), Labs 02–08: 0% (no data)
- **Lab 01 — Group Performance** — top group B25-CSE-02 at 86.9%, bottom group
  B25-CSE-03 at 49.9%

The agent proactively fetched all available data rather than asking which lab,
because the skill teaches it to call `lms_labs` first when no lab is specified,
then act on what it finds. It also offered to trigger the sync pipeline to refresh
stale data.

## Task 2A — Deployed agent

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
