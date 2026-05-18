# Agent Teams

A library of multi-agent teams (agentic workflows) using **Ejentum's RA²R Logic API** as the cognitive layer. Each team is a deployable artifact: drop it into your runtime, configure one credential, run.

The teams in this repo are tuned for specific tasks where multi-cognitive analysis genuinely beats single-agent output. They use **cross-lab agent diversity** (Anthropic, Google, Alibaba, Zhipu, OpenAI) to reduce correlated failure modes that come from any single model family.

---

## Catalog

### [adversarial-code-review](./adversarial-code-review)
A 4-agent team (architect + reasoner + implementer + reviewer) for [heym](https://heym.run) v0.0.9+ that performs deep adversarial code review. Refuses to rubber-stamp PRs, sources every concern from a specialist agent, grounds approvals in specific positive evidence. Each specialist applies a distinct Ejentum cognitive harness (reasoning, code, anti-deception). [→ Setup and verification tests](./adversarial-code-review/README.md)

### [eval](./eval)
Evaluation framework for comparing baseline LLM output against Ejentum-augmented LLM output, with a third-party blind judge. Available as n8n workflows, a Python CLI, and integration patterns for agentic IDEs (Cursor, Antigravity, Claude Code). The instrument is the artifact: import, run on your own prompts, see the diff. [→ Spec and integrations](./eval/README.md)

### [blind-eval-trio](./blind-eval-trio)
A 3-agent team for [heym](https://heym.run) v0.0.20+ that performs **pre-commitment self-evaluation for agent runtimes**. Submit (task, planned method); three blind cross-lab evaluators (steelman defends, stress_test attacks, gap_finder finds what's missing) return three independent perspectives. Calling agent integrates them — no synthesizer. Models cannot reliably self-evaluate; this is the structural fix. Validated across engineering refactors, payments migration, security incident response, investigative reasoning. [→ Setup and verification tests](./blind-eval-trio/README.md)

### [n8n-harness-integration-patterns](./n8n-harness-integration-patterns)
Four ways to wire a reasoning harness into an n8n agent, each with a different control vs. flexibility tradeoff. One importable workflow, one chat trigger, four branches selected by prefix: dynamic system prompt (you pick the mode), reasoner agent (one tool, model decides when), full harness (four tools, model decides which), and ejentum-mcp (single MCP node, same as full harness with smaller footprint). Pick your tradeoff. [→ Setup and the four patterns in detail](./n8n-harness-integration-patterns/README.md)

---

## How these teams use Ejentum

Each agent (or evaluation step) calls the Ejentum Logic API in one of four cognitive modes:

| Mode | Purpose |
|---|---|
| `reasoning` | General reasoning scaffold — failure-mode suppressors, target patterns, falsification tests |
| `code` | Code-specific failure suppressors — cross-layer mismatch, environment drift, invariant violations |
| `anti-deception` | Suppresses sycophancy, hallucination, prompt injection, false certainty |
| `memory` | Perception sharpening, behavioral calibration, cross-turn observation |

Two paths to wire each cognitive mode into a specialist agent:

- **HTTP Request tool** (canonical): the curl pattern shown in each team's README. Works on every runtime.
- **MCP server** (when the runtime supports MCP clients): use [ejentum-mcp](https://github.com/ejentum/ejentum-mcp). Two install paths: stdio via `npx -y ejentum-mcp` for clients that spawn MCP servers as subprocesses (Claude Desktop, Cursor, Windsurf, Codex CLI, Claude Code), or hosted HTTPS at `https://api.ejentum.com/mcp` for HTTP-MCP clients (n8n MCP Client and others). Either way the four harnesses appear as `harness_*` tools your specialist can call directly. No HTTP wiring per agent.

Get an Ejentum API key at [ejentum.com/pricing](https://ejentum.com/pricing). Free tier: 100 calls total.

Read more at [ejentum.com/docs](https://ejentum.com/docs/method).

---

## Adding a new team

The pattern (orchestrator + N specialists, each with a mode-specific harness) generalizes. To contribute or fork a new team:

1. Pick a target task with multi-cognitive value (refactor planning, security audit triage, production debug forensic, spec verification, test design from traces, etc.).
2. Decide which Ejentum modes each specialist needs.
3. Build the workflow on your runtime of choice (heym, n8n, LangGraph, your own).
4. Drop into a new folder here with: `README.md`, workflow file(s), skill MDs (if applicable), system prompts, screenshots.
5. Add a row to the Catalog above.

Future teams in the planning phase: refactor planner, security audit triage, production debug forensic.

---

## License

MIT. See [LICENSE](./LICENSE).

## Contact

**info@ejentum.com**
