# Adversarial Code Review

A multi-agent team that performs **adversarial code review**: refuses to rubber-stamp PRs, sources every concern from a specialist agent (never the orchestrator), and grounds approvals in specific positive evidence rather than absence-of-negatives.

The team uses **cross-lab agent diversity** (Anthropic + Google + Alibaba + Zhipu) and three [Ejentum](https://ejentum.com) cognitive harnesses (reasoning, code, anti-deception) so the review thinks across dimensions instead of producing the smoothed-out average that single agents tend toward.

> **What this is for:** code review of specific changes (diffs, before/after snippets, PR descriptions). Not for general programming questions, architecture brainstorming, or "what should I build" — those are explicitly out of scope and the orchestrator declines them.

---

## Architecture

```
chatInput
   │
   ▼
architectAgent (orchestrator, no cognitive tool)
   │  classifies + decomposes + integrates
   │
   ├── reasonerAgent       (mode: reasoning)
   ├── implementerAgent    (mode: code)
   └── reviewerAgent       (mode: anti-deception)
```

The architect has NO cognitive harness and NO http tool. It cannot produce concerns from its own reading; every concern in the final verdict must come from a specialist's evidence. This makes the multi-agent value structurally guaranteed instead of theatrical.

---

## Available implementations

| Platform | Status | Path |
|---|---|---|
| **heym** (v0.0.9+) | Live | [heym/](./heym) |
| n8n | Planned | [n8n/](./n8n) |
| Python (standalone) | Planned | [python/](./python) |
| Agentic IDEs (Cursor, Claude Code, Antigravity) | Planned | [agentic_ides/](./agentic_ides) |

The cognitive scaffolding (system prompts + skill files + verification tests) ports verbatim across implementations; only the runtime wiring differs. Open the platform you're using for setup, configuration, and the four verification tests.

---

## License

MIT. See [LICENSE](../LICENSE).

## Contact

**info@ejentum.com**
