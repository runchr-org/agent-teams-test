# Ejentum Evaluation Module

Open-source side-by-side blind evaluation for any OpenAI-compatible LLM, with optional Ejentum cognitive harness wired in as a tool call. Two agents answer the same prompt. A blind judge scores both. Results are revealed only after scoring.

Single HTML file. One stdlib Python proxy. No build step, no framework, no install.

## What it does

You give it:

- An OpenAI-compatible provider (OpenRouter, OpenAI, Anthropic via gateway, vLLM, llama.cpp, anything that speaks the `/chat/completions` shape)
- An agent model
- A judge model (different from the agent, recommended)
- An Ejentum API key (get one at [ejentum.com](https://ejentum.com))
- A prompt to evaluate
- The dimensions you want the judge to score on (defaults: Accuracy, Faithfulness, Held the line)

It runs:

1. **Agent A** (raw): one call to your model with whatever system prompt you write.
2. **Agent B** (raw + harness): same model, same temperature, but with the `ejentum_harness` tool wired in. Agent B shapes a query describing the task, calls the harness, receives a cognitive operation (procedure + reasoning topology + falsification test + suppression signals), internalizes it, then writes its final answer.
3. **Blind judge**: a different model receives only the task and two responses labelled `A` and `B`. No knowledge of which is which. Scores both on your dimensions, returns a verdict.
4. **Reveal**: A/B unblind to "Raw" and "Raw + harness," scores populate, the cognitive posture grids render.

The judge never sees the harness output. The harness agent never sees the judge prompt. The blind is real.

## Quickstart

```bash
git clone https://github.com/ejentum/agent-teams.git
cd agent-teams/agent_evaluation_module_xp95
python serve.py
```

Then open [http://localhost:8000/demo.html](http://localhost:8000/demo.html) in your browser.

In the UI:

1. Paste your provider base URL (e.g. `https://openrouter.ai/api/v1`) and your API key.
2. Wait two seconds. The Agent/Judge model dropdowns auto-populate from the provider's `/models` endpoint.
3. Pick an agent model that supports tool calling (e.g. `google/gemini-2.5-flash`, `openai/gpt-4o-mini`, `anthropic/claude-haiku-4.5`).
4. Pick a different judge model (recommended: `deepseek/deepseek-v3.1` or `anthropic/claude-haiku-4.5`).
5. Paste your Ejentum API key.
6. Pick a harness mode: `reasoning`, `anti-deception`, `code`, or `memory`.
7. Type a prompt and click **Run Evaluation**.

Everything else (system prompts, judge prompt, dimensions, temperatures, demo title) is editable in the UI and persists in localStorage.

## Why a local proxy

The Ejentum gateway does not send CORS headers, so a direct browser fetch is blocked. `serve.py` is a small stdlib Python proxy that forwards `POST /ejentum-proxy` server-side to the gateway. Your API key travels browser → localhost → gateway only, never to any third party.

Any reverse proxy (nginx, Caddy, Cloudflare Workers) that forwards `POST /ejentum-proxy` to the Ejentum gateway and serves `demo.html` as a static file is equivalent in production.

Override the listening port or the gateway URL via environment variables:

```bash
PORT=8080 GATEWAY=https://my-gateway.example.com/logicv1/ python serve.py
```

## What gets persisted

`localStorage` only. Everything stays in the browser:

- Field values (keys, models, prompts, dimensions, temperatures)
- Run history (per-run scores and metadata for the charts)
- Avatars (data-URL encoded)

Nothing is sent to any third party other than your provider, the judge model's provider, and the Ejentum gateway. No telemetry. No analytics. No phone-home.

To wipe all stored state, click **Clear history** in the Results Overview panel and clear all `ejm_*` localStorage entries via DevTools.

## Configuration surfaces

Every prompt, model, dimension, and parameter is editable in the UI. No code edits required.

### Agent A system prompt
Goes only to the raw model. Empty by default. Write whatever framing you want for the baseline.

### Agent B system prompt
Goes only to the harness agent. This is where you teach Agent B what a cognitive operation is and how to use the scaffold it receives as a tool result. Empty by default. A strong starting point is shipped as a placeholder.

### Harness mode
- `anti-deception` (default) — sycophancy, hallucination, prompt injection resistance, 139 operations across 6 sub-layers
- `reasoning` — general reasoning scaffold, 311 cognitive operations across 6 sub-domains
- `code` — code generation, refactoring, architecture, 128 operations
- `memory` — perception sharpening, behavioral calibration, 101 operations

### Dimensions
The judge scores on whatever dimensions you put in the Dimensions panel. Type a name, or pick from the autocomplete library (Accuracy, Faithfulness, Held the line, Reasoning depth, Hallucination resistance, Clarity, Completeness, Safety, Source citing, Tone appropriateness, Format adherence, Conciseness). Max 8 dimensions.

The Judge system prompt uses `{{DIMENSIONS}}` and `{{JSON_SHAPE}}` placeholders so the dimensions block stays in sync with whatever you've configured.

### Temperatures
Agent temperature (default 0.7) and Judge temperature (default 0) are independent. Judge at 0 reduces variance run-to-run; bump it if you want to study judge variance directly.

### Multi-turn scenario mode
Toggle the **Multi-turn scenario mode** checkbox. Paste a sequence of turns separated by `---` on their own lines. The agents accumulate conversation history across turns within the scenario. Useful for evaluating drift, hallucination cascade, and authority-escalation attacks.

## The cognitive posture field

Two 10×10 grids per agent. Pure client-side text analysis. No logprobs required.

- **Confidence** — diverging palette from hedged blue to assertive red. Computes net `(assertion - hedge)` lexical signal per chunk plus punctuation cadence (periods lean assertive, commas lean hedged).
- **Reasoning** — sequential palette from dark to hot. Counts explicit reasoning markers per chunk: `because`, `therefore`, `if/then`, `due to`, `as a result`, etc.

Both grids apply a 2D Gaussian blur post-chunking so sparse markers bleed into organic blob shapes rather than isolated pixels. Heat zones radiate. The whole field is independent of the judge — it is a second signal on the same response.

## Cost note (honest)

The harness branch typically uses 5–10x the tokens of the raw branch. Reason: the harness flow is two model calls (one to shape the query and call the tool, one to write the final response after receiving the scaffold), plus the scaffold itself (~500–1500 tokens depending on mode and operation complexity).

This is not free. Account for it when running large batches. The harness produces measurably better answers in categories where the failure mode is rhetorical or posture-related (sycophancy, multi-turn drift, authority claims, deception). It does not typically help on simple factual queries or knowledge-bound tasks.

## Models known to work

Tool calling support is required for the agent (judge does not need it).

| Provider | Agent model | Judge model |
|---|---|---|
| OpenRouter | `google/gemini-2.5-flash`, `openai/gpt-4o-mini`, `openai/gpt-4.1`, `anthropic/claude-haiku-4.5` | `deepseek/deepseek-v3.1`, `anthropic/claude-haiku-4.5` |
| OpenAI direct | `gpt-4o`, `gpt-4o-mini`, `gpt-4.1` | `gpt-4o-mini` |
| Anthropic via gateway | `claude-haiku-4.5`, `claude-sonnet-4.6` | `claude-haiku-4.5` |

Reasoning-output models (the o-series, Gemini Pro) work but cost more and respond slower. For a fast eval pipeline, prefer flash-class agent models with a stronger judge.

## License

MIT. See [LICENSE](LICENSE).

## Related

- [ejentum.com](https://ejentum.com) — the cognitive harness API
- [ejentum-mcp](https://www.npmjs.com/package/ejentum-mcp) — MCP server (use the harness from Claude Code, Cursor, Antigravity, any MCP host)
- [agent-teams](https://github.com/ejentum/agent-teams) — multi-agent team templates that use the harness
- [Under Pressure (Zenodo)](https://doi.org/10.5281/zenodo.19392715) — empirical research on cognitive harness performance under adversarial conditions
