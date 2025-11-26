# Integration Guide

This document provides copy-ready steps for the two most common setups: VS Code (Copilot Chat) and GitHub Copilot coding agent. Adjust paths and tokens to match your environment.

## 1. VS Code / Copilot Chat (stdio)
1. Install RACAG with MCP support:
   ```bash
   pip install editerra-racag[mcp]
   ```
2. Ensure `.editerra-racag.yaml` exists in the workspace (`editerra-racag init --provider openai`).
3. Add `.vscode/mcp.json` to your repository:
   ```json
   {
     "servers": {
       "racag": {
         "command": "editerra-racag",
         "args": [
           "mcp-server",
           "--workspace", "${workspaceFolder}",
           "--transport", "stdio"
         ],
         "env": {
           "OPENAI_API_KEY": "${OPENAI_API_KEY}",
           "RACAG_AUTH_TOKEN": "${RACAG_AUTH_TOKEN}"
         }
       }
     }
   }
   ```
4. In VS Code, run **MCP: List Servers**, start `racag`, and confirm the tools appear in Copilot Chat’s tool picker (per GitHub Docs: https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-with-mcp#configuring-mcp-servers-in-visual-studio-code).
5. Use Copilot Chat in Agent mode and select RACAG tools when prompted.

### Tool list exposed
- `racag.query` – retrieves ranked chunks + markdown context.
- `racag.superprompt` – returns the curated superprompt block.
- `racag.index` – re-runs chunking/embedding (disable via `--read-only`).
- `racag.watch_tick` – mirrors the local watcher by running an incremental index cycle on demand.
- `racag.stats` – collection metadata for observability.
- `racag.settings.describe` – renders the active config snapshot.

#### When to trigger `watch_tick` vs. `index`
- Run `racag.watch_tick` inside Copilot Chat right after you save or stage changes so embeddings stay close to your working tree. Copilot’s tool picker lets you supply a short reason (e.g., “sync telemetry refactor”).
- Call `racag.index` only when the repository structure changed substantially (new language folders, provider switch, `.editerra-racag.yaml` edits) or when you need to rebuild the entire vector store. Expect it to take longer and potentially pause other tool calls.

## 2. GitHub Copilot coding agent
Repository admins can allow Copilot coding agent to call RACAG by editing the MCP configuration in **Settings → Copilot → Coding agent**.

### 2.1 MCP configuration JSON
```json
{
  "mcpServers": {
    "racag": {
      "type": "local",
      "command": "editerra-racag",
      "args": [
        "mcp-server",
        "--workspace", "./",
        "--transport", "stdio",
        "--read-only"
      ],
      "tools": ["racag.query", "racag.superprompt"],
      "env": {
        "RACAG_AUTH_TOKEN": "COPILOT_MCP_RACAG_AUTH_TOKEN",
        "OPENAI_API_KEY": "COPILOT_MCP_OPENAI_API_KEY"
      }
    }
  }
}
```
Notes:
- Copy the sample into the MCP configuration box. Copilot validates JSON structure on save (GitHub docs: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/extend-coding-agent-with-mcp#adding-an-mcp-configuration-to-your-repository).
- Allowlist only read-only tools at first; add `racag.index` after trust/pilot sign-off.

### 2.2 Environment secrets
1. Navigate to **Settings → Environments → copilot**.
2. Add secrets prefixed with `COPILOT_MCP_`, e.g.:
   - `COPILOT_MCP_RACAG_AUTH_TOKEN`
   - `COPILOT_MCP_OPENAI_API_KEY`
3. Redeploy or re-run Copilot agent tasks so the new secrets propagate (GitHub docs: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/extend-coding-agent-with-mcp#setting-up-a-copilot-environment-for-copilot-coding-agent).

### 2.3 Validation
- Assign a low-risk issue to Copilot. When it opens the “Start MCP Servers” log, verify the RACAG tools list is emitted (per the validation steps in the GitHub docs linked above).
- Watch for `racag.query` / `racag.superprompt` invocations in the session logs to confirm the MCP server is reachable.
- Encourage the agent to run `racag.watch_tick` at the start of each task (mention it in the issue description or acceptance criteria). Reserve `racag.index` for post-merge cleanups or when you detect stale embeddings across many directories.

### 2.4 Remote HTTP/SSE endpoint (shared service)
If you prefer to centralize RACAG instead of launching it per-repository, point Copilot (or any MCP host) at the HTTP transport:
```json
{
  "mcpServers": {
    "racag": {
      "type": "http",
      "url": "https://racag.example.com/invoke",
      "sseUrl": "https://racag.example.com/invoke/stream",
      "headers": {
        "Authorization": "Bearer ${COPILOT_MCP_RACAG_AUTH_TOKEN}"
      },
      "tools": ["racag.query", "racag.superprompt"],
      "timeout": 60
    }
  }
}
```
Notes:
- Ensure your deployment runs `editerra-racag mcp-server --transport http --host 0.0.0.0 --port 8123 --auth-mode bearer --auth-token <value>` (Docker, Kubernetes, or systemd samples in `DEPLOY.md`).
- Terminate TLS at the service or a reverse proxy, and expose only `/invoke` and `/invoke/stream`.
- Copilot secrets must still be prefixed with `COPILOT_MCP_`; map them to the `headers.Authorization` placeholder as shown above.
- If you prefer mutual TLS instead of bearer headers, launch the server with `--auth-mode mtls` or `--auth-mode hybrid` plus `--tls-cert`, `--tls-key`, and `--tls-ca` path arguments, then omit the `Authorization` header in the MCP config (the TLS handshake enforces identity).
- Long-running services can export `RACAG_AUTH_MODE`, `RACAG_TLS_CERT`, `RACAG_TLS_KEY`, and `RACAG_TLS_CA` environment variables instead of repeating CLI flags.

### 2.5 Sample GitHub Actions workflow
- See `.github/workflows/copilot-agent-sample.yml` for a copy/paste workflow that installs `editerra-racag[mcp]`, verifies the MCP entrypoints, and produces a ready-to-import `mcp.json` artifact for Copilot coding agent repositories.
- Before running it, add repository secrets such as `COPILOT_MCP_OPENAI_API_KEY` and `COPILOT_MCP_RACAG_AUTH_TOKEN`, or edit the workflow to point at your preferred secret names.
- Trigger it via **Run workflow** (manual dispatch) whenever you need to validate that runners can provision dependencies before enabling MCP tools in Copilot’s settings.

## 3. Claude Desktop / other clients
- Point the `command` to `editerra-racag mcp-server --workspace /ABS/PATH --transport stdio` in the client’s MCP config file (e.g., `~/Library/Application Support/Claude/claude_desktop_config.json`).
- Make sure you set `OPENAI_API_KEY`/`RACAG_AUTH_TOKEN` in Claude Desktop’s environment before launching it.

## 4. Troubleshooting checklist
- **Server fails to start:** ensure Python 3.10 and `modelcontextprotocol[cli]>=1.2.0` are installed.
- **Tools not visible:** re-run **MCP: List Servers** and look for JSON errors in `.vscode/mcp.json`.
- **Copilot agent logs show “permission denied”:** confirm `COPILOT_MCP_*` secrets are mapped to the `env` keys in the MCP JSON.
- **Client cannot connect over HTTPS:** ensure the certificate paths passed via `--tls-cert/--tls-key/--tls-ca` exist inside the container/host and that clients trust the issuing CA.
- **Indexing tool disabled:** remove `--read-only` or set `allow_index=true` in Docker/Kubernetes manifests when you want remote re-index capability.

Refer to `SECURITY.md` for firewall, TLS, and authentication recommendations before exposing the server outside localhost.
