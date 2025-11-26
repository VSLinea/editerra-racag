# Changelog

All notable changes to this project are documented here. This file follows the
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format and uses
[Semantic Versioning](https://semver.org/) for release tags. When you cut a
`vX.Y.Z` tag, summarize the highlights under a matching section so the release
workflow can link to it.

## [Unreleased]
### Added
- Placeholder for upcoming work.

## [v0.2.0] - 2025-11-26
### Added
- Telemetry event helper (`editerra_racag/telemetry/events.py`) and instrumentation for the watcher, MCP transport, and CLI flows so operators can trace incremental indexing.
- MCP/CLI/deployment regression tests (`tests/test_mcp_server.py`, `tests/test_cli_entrypoint.py`, `tests/test_deployment_artifacts.py`) plus CI matrix coverage across Python 3.10/3.11 (extras included).
- Release documentation (README 📦 section, docs/mcp/DEPLOY.md, docker-compose, Kubernetes manifests) pointing to the GHCR-hosted MCP image.
- Keep-a-Changelog template to capture highlights for every tag.

### Changed
- Default Docker Compose and Kubernetes manifests now pull `ghcr.io/vslinea/editerra-racag-mcp:latest` instead of building locally.
- README status checklist marks the PyPI package and MCP server as shipped, and adds PyPI/GHCR badges.

### Operational Notes
- Tag `v0.2.0-rc1` (or similar) first to dry-run the release workflow and verify PyPI/GHCR credentials, then push the final `v0.2.0` tag once the RC succeeds.

## [v0.1.0] - 2025-11-19
### Added
- Release workflow that builds wheels/SDists, uploads artifacts, and publishes to PyPI/ GHCR on `v*` tags.
- README release badges plus deployment docs referencing the published container registry image.

### Operational Notes
- Push a pre-release tag such as `v0.1.0-rc1` to dry-run the pipeline and verify PyPI/GHCR credentials before the public tag.
