# Adversarial Code Review — n8n

**Status:** planned. Not yet shipped.

n8n port of the adversarial code review team. Until this folder is populated, the [heym version](../heym/) is the canonical implementation.

## Architecture port (planned)

n8n's AI Agent node + tools differs from heym's multi-agent orchestration:

- **Sub-agent delegation:** heym has `isOrchestrator: true` + `subAgentLabels` as first-class primitives. n8n doesn't have native sub-agent delegation. The orchestrator-and-three-specialists pattern will be built with multiple n8n AI Agent nodes connected via Set/IF logic, or via OpenAI's tool-calling API where each specialist is exposed as a tool.
- **HTTP-as-tool:** heym's node-as-tool with agent-provided cURL has a direct n8n analog. n8n's HTTP Request node wires cleanly as an AI Agent tool. The cognitive harness call works essentially identically.
- **Architect-cannot-skip-delegation invariant:** harder to enforce structurally in n8n. May require stronger system-prompt language to compensate for the missing structural guarantee.

## What this folder will contain when ready

- `workflow.json` — n8n workflow export
- `screenshots/` — canvas screenshots
- `README.md` — setup steps + the four verification tests adapted to n8n's invocation model
- `code_nodes/` — any custom JS code nodes (if needed for response shaping)

The cognitive scaffolding (system prompts + skill files) ports verbatim from `../heym/`. Only the runtime wiring changes.
