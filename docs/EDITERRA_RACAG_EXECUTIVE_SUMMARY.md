# Editerra RAC-CAG - Executive Summary

**Date:** November 19, 2025  
**Product:** Editerra RAC-CAG Coding Assistant  
**Status:** Ready to Build  

---

## TL;DR - What We're Building

**Editerra RAC-CAG** is a commercial AI coding assistant that understands your entire codebase and provides intelligent context to ANY AI tool (Copilot, Claude, ChatGPT, local LLMs).

**Key Differentiators:**
- 🎯 Works with ANY LLM (not locked to OpenAI)
- 🔒 Privacy-first (local database)
- 📦 Three deployment methods (Python CLI, VS Code extension, MCP server)
- 💰 Monetizable (Business Source License)
- ⚡ Advanced hybrid scoring (better than pure vector search)

---

## Your Decisions

✅ **Name:** Editerra RAC-CAG Coding Assistant  
✅ **License:** Business Source License 1.1 → Apache 2.0 (after 3 years)  
✅ **Repository:** New GitHub repo under VSLinea  
✅ **LLM Support:** Multi-provider (OpenAI, Claude, Azure, Ollama, etc.)  
✅ **Priority:** All three deployment types (Python + VS Code + MCP)  
✅ **Business Model:** Freemium (free for <10 devs, paid for enterprises)  

---

## Three Deployment Types

### 1. Python Package (`pip install editerra-racag`)
**Who:** Developers, power users, CI/CD pipelines  
**Use Case:** Command-line tool, automation, scripting  
```bash
editerra-racag init
editerra-racag index
editerra-racag query "Where is authentication?"
```

### 2. VS Code Extension (`editerra.racag`)
**Who:** All VS Code users  
**Use Case:** Seamless IDE integration, Copilot enhancement  
**Features:**
- One-click workspace indexing
- Status bar integration
- Copilot context injection
- Real-time file watching

### 3. MCP Server (`editerra-racag-mcp`)
**Who:** Claude Desktop, Cline, Continue.dev users  
**Use Case:** AI assistant integration via Model Context Protocol  
**Features:**
- `query_codebase` tool
- `index_workspace` tool
- Works with any MCP client

---

## Business Source License (BSL) Summary

**Free For:**
- ✅ Individual developers (unlimited)
- ✅ Small teams (< 10 developers)
- ✅ Open source projects
- ✅ Educational use

**Paid License Required For:**
- ⚠️ Teams with 10+ developers
- ⚠️ Offering as a hosted/managed service
- ⚠️ Enterprise deployments

**After 3 Years (2028-11-19):**
- 🎉 Automatically converts to Apache 2.0
- 🎉 Becomes fully open source
- 🎉 All restrictions removed

**Why BSL?**
- Protects your commercial opportunity
- Still allows source code visibility
- Used by HashiCorp, CockroachDB, Sentry
- Ensures eventual open source conversion

---

## Revenue Model

### Pricing Tiers

| Tier | Price | Target | Features |
|------|-------|--------|----------|
| **Free** | $0 | Individuals, small teams (<10 devs) | All core features, community support |
| **Pro** | $19/user/month | Teams (10-100 devs) | Priority support, private LLMs, analytics |
| **Enterprise** | Custom | Large organizations (100+ devs) | White-label, on-premise, SLA, custom integration |
| **Cloud Hosted** | +$9/user/month | All tiers | Managed infrastructure, included API credits |

### Projected Revenue

| Timeline | Free Users | Paid Users | Revenue |
|----------|-----------|-----------|---------|
| **Month 1** | 1,000 | 10 | ~$2,000 |
| **Month 3** | 5,000 | 50 | ~$10,000 |
| **Month 6** | 10,000 | 150 | ~$30,000 |
| **Year 1** | 50,000 | 500 | ~$114,000 |
| **Year 2** | 150,000 | 2,000 | ~$456,000 |
| **Year 3** | 300,000 | 5,000 | ~$1.1M |

*Conservative estimates based on similar developer tools*

---

## Multi-LLM Architecture

### Supported Providers (Day 1)
1. **OpenAI** (default) - GPT-4, text-embedding-3-large
2. **Ollama** (free, local) - llama3.1, nomic-embed-text

### Supported Providers (Future)
3. **Anthropic** - Claude 3.5, Voyage embeddings
4. **Azure OpenAI** - Enterprise deployment
5. **Google Vertex AI** - Gemini, text-embedding-004
6. **AWS Bedrock** - Claude, Titan
7. **Cohere** - Command-R, embed-english-v3.0

### Provider Abstraction
```python
class LLMProvider(ABC):
    def embed(self, texts: List[str]) -> List[List[float]]
    def rerank(self, query: str, candidates: List[str]) -> List[float]
```

Users choose their provider in `.editerra-racag.yaml`:
```yaml
llm_provider: "ollama"  # or openai, anthropic, etc.
```

---

## Technical Architecture

### Current RACAG (in KairosAmiqo)
```
[Source Files] → [Chunking] → [OpenAI Embedding] → [ChromaDB] → [Query + Rerank] → [Context]
```

**Issues:**
- ❌ Hardcoded paths (`/Users/lyra/KairosMain/...`)
- ❌ Fixed collection name (`kairos_chunks`)
- ❌ OpenAI-only
- ❌ No configuration system

### Editerra RAC-CAG (Target)
```
[Any Project] → [Auto-detect] → [Config] → [Chunking] → [ANY LLM] → [Local DB] → [Query] → [Context]
```

**Improvements:**
- ✅ Dynamic workspace detection
- ✅ Project-specific configuration
- ✅ Multi-LLM support
- ✅ Portable, reusable
- ✅ Three deployment options

---

## Development Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **Phase 1** | Week 1 | Core refactoring, multi-LLM support |
| **Phase 2** | Week 2 | Python package + CLI |
| **Phase 3** | Week 3-4 | VS Code extension |
| **Phase 4** | Week 5 | MCP server |
| **Phase 5** | Week 6 | Documentation + marketing |
| **Phase 6** | Week 7-8 | Polish + launch |

**Target Launch Date:** ~6-8 weeks from now (early January 2026)

---

## Immediate Next Steps (This Week)

### Day 1 (Today) ✅
- [x] Complete analysis
- [x] Choose name: "Editerra RAC-CAG"
- [x] Choose license: BSL 1.1
- [x] Define deployment strategy: All three types
- [ ] Create GitHub repo: `github.com/VSLinea/editerra-racag`

### Day 2-3
- [ ] Copy RACAG code from KairosAmiqo
- [ ] Refactor: `racag` → `editerra_racag`
- [ ] Create configuration system
- [ ] Remove hardcoded paths

### Day 4-5
- [ ] Multi-LLM provider abstraction
- [ ] Implement OpenAI provider
- [ ] Implement Ollama provider
- [ ] Test provider switching

### Day 6-7
- [ ] CLI interface (init, index, query)
- [ ] Unit tests
- [ ] Documentation
- [ ] Tag v0.1.0-alpha

---

## Key Files Created

All planning documents are in your KairosAmiqo workspace:

1. **`RACAG_STANDALONE_ANALYSIS.md`**  
   Complete technical analysis, architecture, competitive landscape

2. **`EDITERRA_RACAG_IMPLEMENTATION_PLAN.md`**  
   Week-by-week implementation roadmap with detailed tasks

3. **`EDITERRA_RACAG_LICENSE_EXPLAINED.md`**  
   Business Source License 1.1 full text and FAQ

4. **`EDITERRA_RACAG_QUICKSTART.md`**  
   Immediate action items and setup instructions

5. **`EDITERRA_RACAG_EXECUTIVE_SUMMARY.md`** ← You are here  
   High-level overview for quick reference

---

## Success Metrics

### Launch (Week 1)
- 100+ GitHub stars
- 50+ installs
- 5+ positive reviews

### Month 1
- 1,000+ GitHub stars
- 500+ VS Code installs
- Featured in VS Code marketplace
- 10+ blog mentions

### Month 3
- 5,000+ stars
- 2,000+ installs
- First 5 paid customers
- $5,000+ MRR

### Year 1
- 50,000+ users
- 500+ paid customers
- $114,000+ ARR
- Self-sustaining business

---

## Risk Management

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Low adoption | Medium | Great docs, demos, marketing |
| LLM costs too high | Medium | Support free local models (Ollama) |
| Technical complexity | Low | Pre-built binaries, sensible defaults |
| Competition | Medium | Unique features (hybrid scoring, multi-LLM) |
| License pushback | Low | Clear terms, eventual open source |

---

## Competitive Advantages

**vs. GitHub Copilot:**
- ✅ Works with ANY AI tool, not just Copilot
- ✅ Full codebase awareness (not just open files)
- ✅ Hybrid AI scoring (better context selection)

**vs. Cursor:**
- ✅ Works in VS Code (no need to switch editors)
- ✅ Open source (BSL → Apache 2.0)
- ✅ Choose your own LLM

**vs. Continue.dev:**
- ✅ Simpler setup
- ✅ Better indexing (tree-sitter based)
- ✅ Professional support available

**vs. Sourcegraph:**
- ✅ AI-native (not just search)
- ✅ Hybrid scoring
- ✅ Easier to deploy

---

## What Makes This Valuable?

1. **Solves Real Pain:** Large codebases are hard for AI to understand
2. **Multi-Platform:** Works everywhere (CLI, IDE, AI assistants)
3. **Provider-Agnostic:** Not locked to one LLM vendor
4. **Privacy-First:** Local database, no cloud dependency
5. **Monetizable:** Clear path to revenue with BSL license
6. **Community-Friendly:** Eventually becomes open source

---

## Questions Answered

✅ **Name?** Editerra RAC-CAG Coding Assistant  
✅ **Repository?** New GitHub repo under VSLinea  
✅ **License?** Business Source License 1.1  
✅ **LLM Support?** Multi-provider from day 1  
✅ **Priority?** All three deployment types  
✅ **Timeline?** 6-8 weeks to v1.0  
✅ **Business Model?** Freemium with enterprise licensing  

---

## Ready to Start?

**Next Command:**
```bash
# Create the GitHub repo
open https://github.com/organizations/VSLinea/repositories/new

# Name: editerra-racag
# Description: AI-Powered Code Intelligence for Complex Projects
# Public
# Don't initialize with README

# Then follow EDITERRA_RACAG_QUICKSTART.md
```

---

**Let's build this! 🚀**

Got questions? Check the other planning documents or ask Copilot.

---

**Documents Index:**
- 📊 This summary
- 🔬 `RACAG_STANDALONE_ANALYSIS.md` - Deep technical analysis
- 📋 `EDITERRA_RACAG_IMPLEMENTATION_PLAN.md` - Week-by-week roadmap
- ⚖️ `EDITERRA_RACAG_LICENSE_EXPLAINED.md` - Legal details
- 🚀 `EDITERRA_RACAG_QUICKSTART.md` - Get started now

**Contact:** VSLinea Team
**Email:** support@editerra.io (set this up!)
**GitHub:** https://github.com/VSLinea/editerra-racag (create this!)

---

*Made with ❤️ and lots of planning*
