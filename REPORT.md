# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

### Checkpoint 1: "What is the agentic loop?"

Command: `cd nanobot && uv run nanobot agent --logs --session cli:task1a-loop -c ./config.json -m "What is the agentic loop?"`

Agent response:

> The agentic loop is the core cycle that an AI agent follows to accomplish tasks autonomously. Here's how it works:
>
> ```
> ┌─────────────┐
> │  Observe    │ ← Receive user input, tool outputs, environment state
> └──────┬──────┘
>         ▼
> ┌─────────────┐
> │  Think      │ ← Reason about what to do next (plan, decide)
> └──────┬──────┘
>         ▼
> ┌─────────────┐
> │  Act        │ ← Call tools, execute commands, modify files
> └──────┬──────┘
>         ▼
> ┌─────────────┐
> │  Observe    │ ← Get results from the action
> └──────┬──────┘
>         ▼
>    (repeat until goal is reached)
> ```
>
> In practice, for me (nanobot), the loop looks like:
>
> 1. Observe — Read your message and understand the request
> 2. Think — Decide what tools or steps are needed (e.g., "I should read this file first")
> 3. Act — Call a tool (like read_file, exec, web_search)
> 4. Observe — See the tool's output
> 5. Think — Analyze the result and decide the next step
> 6. Act — Take the next action (or respond if done)
>
> This repeats until the task is complete or I need to ask you for clarification.
>
> Key principles of a good agentic loop:
> - State intent before acting — explain what you're about to do
> - Never predict results — wait for actual tool output before drawing conclusions
> - Verify after acting — re-read files, check outputs, confirm success
> - Handle failures gracefully — if a tool fails, analyze the error and try a different approach
>
> This is what separates an agent from a simple chatbot — the ability to take actions, observe results, and iterate toward a goal.

### Checkpoint 2: "What labs are available in our LMS?"

Command: `cd nanobot && uv run nanobot agent --logs --session cli:task1a-labs -c ./config.json -m "What labs are available in our LMS?"`

> Note: At this stage (Part A), the agent has MCP tools configured but this checkpoint verifies the agent returns data. On the very first run before MCP was added, the agent read local repo files (README.md, task markdown) and listed lab titles from documentation rather than live API data.
>
> With MCP now configured, the agent calls `lms_labs` and returns real lab names:
>
> ```
> ID  Title
> ───────────────────────────────────────────────────────────
> 1   Lab 01 – Products, Architecture & Roles
> 2   Lab 02 — Run, Fix, and Deploy a Backend Service
> 3   Lab 03 — Backend API: Explore, Debug, Implement, Deploy
> 4   Lab 04 — Testing, Front-end, and AI Agents
> 5   Lab 05 — Data Pipeline and Analytics Dashboard
> 6   Lab 06 — Build Your Own Agent
> 7   Lab 07 — Build a Client with an AI Coding Agent
> 8   lab-08
>
> There are 8 labs in total. Let me know if you'd like details on any specific lab — I can check pass rates, completion rates, top learners, group performance, or submission timelines!
> ```

## Task 1B — Agent with LMS tools

### Checkpoint 1: "What labs are available?"

Command: `cd nanobot && uv run nanobot agent --logs --session cli:task1b-labs -c ./config.json -m "What labs are available?"`

Agent response:

> ```
> Here are the available labs:
>
> ID  Title
> ───────────────────────────────────────────────────────────
> 1   Lab 01 – Products, Architecture & Roles
> 2   Lab 02 — Run, Fix, and Deploy a Backend Service
> 3   Lab 03 — Backend API: Explore, Debug, Implement, Deploy
> 4   Lab 04 — Testing, Front-end, and AI Agents
> 5   Lab 05 — Data Pipeline and Analytics Dashboard
> 6   Lab 06 — Build Your Own Agent
> 7   Lab 07 — Build a Client with an AI Coding Agent
> 8   lab-08
>
> Let me know if you'd like details on any specific lab — I can check pass rates, completion rates, group performance, top learners, or submission timelines!
> ```

### Checkpoint 2: "Is the LMS backend healthy?"

Command: `cd nanobot && uv run nanobot agent --logs --session cli:task1b-health -c ./config.json -m "Is the LMS backend healthy?"`

Agent response:

> ```
> Yes, the LMS backend is healthy! ✅
>
> • Status: Healthy
> • Item count: 56
> ```

The agent called the `lms_health` MCP tool and returned real data from the backend (56 items).

## Task 1C — Skill prompt

### Checkpoint: "Show me the scores" (without specifying a lab)

Command: `cd nanobot && uv run nanobot agent --logs --session cli:task1c -c ./config.json -m "Show me the scores"`

Agent response:

> ```
> I'll check what labs are available in the LMS first.
> ```
>
> (Tool call: `mcp_lms_lms_labs({})`)
>
> ```
> Here are the available labs. Which one would you like to see scores for?
> ```
>
> (Tool call: `mcp_webchat_ui_message(...)` — interactive choice UI)
>
> ```
> Here are the available labs:
>
>  1 Lab 01 – Products, Architecture & Roles
>  2 Lab 02 — Run, Fix, and Deploy a Backend Service
>  3 Lab 03 — Backend API: Explore, Debug, Implement, Deploy
>  4 Lab 04 — Testing, Front-end, and AI Agents
>  5 Lab 05 — Data Pipeline and Analytics Dashboard
>  6 Lab 06 — Build Your Own Agent
>  7 Lab 07 — Build a Client with an AI Coding Agent
>  8 Lab 08 — lab-08
>
> Which lab would you like to see scores for?
> ```

With the LMS skill loaded, the agent correctly called `lms_labs` first (as the skill instructs: "if the user asks for scores, pass rates, completion, groups, timeline, or top learners without naming a lab, call `lms_labs` first"), then presented the available labs and asked the user to choose one. This is the expected behavior — the skill prevents the agent from guessing or returning stale data, and instead prompts the user for clarification.

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
