# Blind Eval Trio

A 3-agent multi-agent team that performs **pre-commitment self-evaluation for agent runtimes**: an external blind cross-lab evaluation primitive that any coding agent or autonomous loop can call before committing to a non-trivial decision.

The team uses **cross-lab agent diversity** (Anthropic + OpenAI + Zhipu) and three [Ejentum](https://ejentum.com) cognitive harnesses (reasoning, anti-deception, memory) so each evaluator thinks through a different cognitive lens. Each agent is locked to a different role — steelman defends, stress_test attacks, gap_finder finds what's missing.

> **The thesis:** Models cannot reliably self-evaluate. Asking the same model to critique its own plan reproduces the original blind spots. The structural fix is external, blind, cross-lab evaluation: three different model labs (different RLHF priors, different training distributions) playing structured adversarial roles, returning three independent perspectives that the calling agent integrates.

> **What this is for:** any agent runtime that needs pushback before committing to a non-trivial decision — coding agents (Claude Code, Cursor, Codex Cloud), autonomous agent loops, multi-agent systems, ops automation, security incident response, strategic decisions. **Not for:** per-step linting (latency 50-80s, cost 3 LLM calls + 3 harness calls per invocation makes this a high-stakes-decisions tool, not a continuous-feedback tool).

---

## Architecture

```
chatInput / webhook
   │
   ▼
   ┌── steelmanAgent     (lab: OpenAI,    harness: reasoning)
   ├── stresstestAgent   (lab: Anthropic, harness: anti-deception)
   └── gapfinderAgent    (lab: Zhipu,     harness: memory)
   │
   ▼
setFields  (non-LLM Output node, structures 3 raw evaluations as JSON)
   │
   ▼
{ steelman, stress_test, gap_finder, usage_note }
```

Three agents run in parallel. Each is locked by system-prompt rule to one role and one cognitive harness — agents structurally cannot smuggle critique into steelman or strengths into stresstest. **No synthesizer agent.** The three evaluations are returned raw, and the calling agent integrates them. Flattening the disagreement via consensus would defeat the purpose; the integration tension between voices IS the value.

The architecture works because three properties hold simultaneously:

1. **Cross-lab decorrelation** — three different RLHF priors and training distributions reduce correlated failure modes
2. **Tool lockout per role** — each agent calls only its assigned harness, no role-switching
3. **Forced output structure** — named sections + severity tags + articulation-quality gate make rubber-stamping structurally hard
4. **No synthesizer** — three raw outputs prevent a final agent from overriding the disagreement

Empirical validation (cross-domain dogfood): the workflow produced expert-level analysis on engineering refactors, payments migration decisions, security incident response, investigative reasoning, and meta-evaluation of its own product viability — without any domain-specific tuning.

---

## Available implementations

| Platform | Status | Path |
|---|---|---|
| **heym** (v0.0.20+) | Live | [heym/](./heym) |
| n8n | Planned | — |
| Python (standalone) | Planned | — |

The system prompts + verification tests port across runtimes; only the orchestration wiring differs.

---

## Calling from any agent runtime

Once deployed, the workflow is callable as an HTTP endpoint via heym's `/api/workflows/{id}/execute/stream` route. Any external agent can curl it directly. A planned MCP wrapper (`blind_eval` tool inside `ejentum-mcp`) will provide a one-install integration for MCP-compatible agent runtimes.

---

## License

MIT. See [LICENSE](../LICENSE).

## Contact

**info@ejentum.com**
