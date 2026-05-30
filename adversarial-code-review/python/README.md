# Adversarial Code Review — Python (standalone)

**Status:** planned. Not yet shipped.

A pure-Python orchestrator port of the adversarial code review team. Until this folder is populated, the [heym version](../heym/) is the canonical implementation.

## Architecture port (planned)

Will use the same orchestrator pattern as [`agent-teams/eval/python/orchestrator.py`](../../eval/python/orchestrator.py), adapted for code review specifically:

- **Architect:** a pure orchestration loop that classifies the PR, decomposes review angles, delegates to three specialists in parallel via async I/O (asyncio.gather), integrates evidence into the structured verdict schema.
- **Specialists:** each is a function that (1) calls an LLM API (Anthropic / Google / OpenRouter) with the system prompt + skill content prepended, (2) calls the Ejentum API to absorb its scaffold, (3) produces output in the team's structured format.
- **Output:** same VERDICT / CHANGE_CLASSIFICATION / FRAMING_NOTES / CONCERNS schema as the heym version.

Zero runtime dependencies beyond the standard library + an HTTP client (httpx or requests). No agent framework needed; the orchestrator IS the framework.

## What this folder will contain when ready

- `orchestrator.py` — main entry point
- `system_prompts/` — per-agent system prompt files (copied verbatim from `../heym/system_prompts.md`, split per agent)
- `skills/` — same skill MDs as the heym version
- `requirements.txt` (or `pyproject.toml`)
- `.env.example` — required keys (per-LLM-provider + Ejentum)
- `README.md` — setup + invocation examples
- `tests/` — the four verification cases as runnable Python tests

Same cognitive scaffolding as [heym/](../heym/); same verification test set; same structured verdict.
