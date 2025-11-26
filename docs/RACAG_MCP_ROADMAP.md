# RACAG MCP Finalization Roadmap

Use this document to track remaining work required to ship the MCP server as a production-ready add-on. Each numbered item corresponds to a milestone with sub-steps.

## 1. Transport & Auth Expansion
1.1 Implement HTTP/SSE transport layer for `RACAGMCPServer`, including routing and streaming responses beyond stdio.
1.2 [x] Add bearer/mTLS authentication options (token validation, cert paths, config toggles) and document usage.
1.3 [x] Update Docker/Kubernetes artifacts to expose the new port with TLS/offload guidance (reverse proxy notes, env vars).
1.4 [x] Regression-test stdio vs. HTTP/SSE pathways to ensure feature parity.

## 2. Incremental Indexing & Watcher Tools
2.1 [x] Refactor the watcher to operate on arbitrary workspaces (remove hardcoded Swift paths, integrate with config).
2.2 [x] Expose an MCP tool such as `racag.watch_tick` (or `racag.refresh_files`) that triggers incremental indexing runs.
2.3 [x] Document when to use the watcher tool vs. full `racag.index`, including Copilot/VS Code examples (see `docs/mcp/README.md` + `docs/mcp/INTEGRATION_GUIDE.md`).
2.4 [x] Add observability hooks (logs/metrics) for watch-driven refreshes so operators can monitor indexing health (see telemetry logs in `docs/mcp/README.md`).

## 3. Quality Gates & Packaging
3.1 [x] Add unit/integration tests covering MCP tool schemas, CLI entrypoint, Docker build, and Kubernetes manifest validation (see `tests/test_mcp_server.py`, `tests/test_cli_entrypoint.py`, `tests/test_deployment_artifacts.py`).
3.2 [x] Expand CI to run across Python 3.10/3.11 and ensure optional extras (`[mcp]`, `[all]`) install cleanly (see `.github/workflows/ci.yml`).
3.3 [x] Publish versioned Docker images/wheels (see `.github/workflows/release.yml`, GHCR badges, and README release section).
3.4 [x] Provide a sample GitHub Actions workflow (`.github/workflows/copilot-agent-sample.yml`) showing how Copilot coding agent repos install RACAG dependencies.

## 4. Docs, Demos, and Assets
4.1 Capture VS Code and Copilot coding agent screenshots demonstrating MCP tool usage; store under `docs/mcp/assets/`.
4.2 Produce a short demo log or transcript walking through Copilot issue assignment → RACAG query → PR generation.
4.3 Update MCP docs to embed visuals and HTTP/SSE instructions (README, DEPLOY, INTEGRATION_GUIDE, SECURITY).
4.4 Publish a quickstart/template repository or sample config to help new teams bootstrap.

## 5. Adoption & Feedback Loop
5.1 Recruit 1–2 pilot organizations, guide them through deployment, and collect structured feedback.
5.2 Triage feedback into the backlog (bugs vs. feature requests) and prioritize blocking issues.
5.3 Finalize pricing/licensing messaging for the MCP add-on tier and reflect it in README/docs.
5.4 Announce GA once pilots are satisfied and remaining critical bugs are resolved.

---
Update this file as items progress (e.g., mark `[x]` or add notes) so everyone can see the current MCP launch status.
