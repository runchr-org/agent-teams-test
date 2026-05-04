# Adversarial Code Review — Agentic IDE Integration

**Status:** planned. Not yet shipped.

Integration patterns for invoking the adversarial code review team from agentic IDEs: Cursor, Claude Code, Antigravity, Cline, and similar tools that support calling external services from inside the agent loop.

## Integration approach (planned)

The IDE's agent calls the deployed code review team — running on heym, as a Python service, or as an MCP server — when the user asks for a code review on a file, diff, or change.

Three patterns to support:

1. **HTTP call from the IDE agent.** The IDE's agent constructs a cURL/fetch with the diff as the input, gets the structured verdict back, surfaces it in the IDE's chat. Works on any IDE that supports HTTP-from-tool-call.
2. **Slash command / skill file.** A pre-built slash command (`/review`) or skill file that the IDE auto-loads, encoding the invocation pattern so the user doesn't have to write the cURL.
3. **MCP server.** Wrap the team's HTTP endpoint as an MCP server; the IDE connects to it via standard MCP transport (stdio or SSE) and gets the team as a callable tool.

## What this folder will contain when ready

- `claude_code/` — slash command + Skill file for Claude Code
- `cursor/` — Cursor rule file + invocation pattern
- `antigravity/` — Antigravity integration recipe
- `mcp_server/` — generic MCP wrapper (stdio + SSE) for any MCP-capable IDE
- Generic invocation pattern documented for IDEs not explicitly listed

Until then, the [heym version](../heym/) can already be triggered manually via heym's chat tab. heym workflows also expose an auto-generated webhook URL (visible via the workflow's "Run with cURL" button) that any agent or script can POST to.
