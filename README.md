# Editerra RAC-CAG Coding Assistant

> AI-Powered Code Intelligence for Complex Projects

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE.md)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://python.org)
[![Status](https://img.shields.io/badge/status-alpha-orange)](https://github.com/VSLinea/editerra-racag)

## 🚀 What is Editerra RAC-CAG?

**Editerra RAC-CAG** (Retrieval-Augmented Context-Aware Generator) is a sophisticated code intelligence engine that helps AI understand your entire codebase - not just the files you have open.

## ⚡ Installation (One Command!)

```bash
# Install everything automatically
pip install editerra-racag
```

**That's it!** All dependencies auto-install:
- ✅ Vector database (ChromaDB)
- ✅ LLM clients (OpenAI, Ollama)
- ✅ Code parsers (tree-sitter)
- ✅ API server (FastAPI)
- ✅ CLI tools
- ✅ ~20 Python packages

**No Docker. No complex setup. No manual configuration.**

### Key Features

- 🧠 **Deep Codebase Understanding** - Vectorizes your entire project using advanced chunking
- 🔍 **Smart Context Retrieval** - Hybrid AI scoring (cosine similarity + LLM reranking)
- 🤖 **Works with ANY LLM** - OpenAI, Anthropic, Azure, Ollama (local/free), and more
- 📦 **Three Ways to Use** - Python CLI, VS Code Extension, or MCP Server
- 🔒 **Privacy-First** - All data stored locally in ChromaDB
- ⚡ **Real-Time Updates** - Incremental indexing as you code
- 🌍 **Multi-Language** - Python, TypeScript, Swift, Java, Go, and more

## 🎯 Quick Start

### Python Package (CLI)

```bash
# Install
pip install editerra-racag

# Initialize in your project
cd /path/to/your/project
editerra-racag init

# Index your codebase
editerra-racag index

# Query your codebase
editerra-racag query "Where is authentication handled?"

# Start watching for changes
editerra-racag watch
```

### VS Code Extension

1. Install from [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=editerra.racag) *(coming soon)*
2. Open any project
3. Run: **"Editerra RAC-CAG: Index Workspace"**
4. Start coding with enhanced AI context!

### MCP Server (for Claude Desktop)

```json
{
  "mcpServers": {
    "editerra-racag": {
      "command": "editerra-racag-mcp",
      "args": ["--workspace", "${workspaceFolder}"],
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

## 🔥 Why Editerra RAC-CAG?

| Problem | Solution |
|---------|----------|
| AI only sees open files | **Indexes entire codebase** |
| Generic vector search is dumb | **Hybrid scoring** (cosine + LLM) |
| Locked to one AI provider | **Multi-LLM support** (OpenAI, Claude, Ollama) |
| Privacy concerns | **Local-first** (ChromaDB on disk) |
| Expensive API calls | **Free option** (Ollama local models) |

## 📊 How It Works

```
┌─────────────┐
│ Your Code   │
└──────┬──────┘
       │ 1. Chunking (tree-sitter)
       ▼
┌─────────────┐
│ Semantic    │
│ Chunks      │
└──────┬──────┘
       │ 2. Embedding (LLM of choice)
       ▼
┌─────────────┐
│ ChromaDB    │
│ (Local)     │
└──────┬──────┘
       │ 3. Query + Rerank
       ▼
┌─────────────┐
│ Smart       │
│ Context     │──▶ GitHub Copilot, Claude, ChatGPT
└─────────────┘
```

## 🛠️ Supported Languages

✅ Python  
✅ TypeScript / JavaScript  
✅ Swift  
✅ Java  
✅ Go  
✅ Rust  
✅ C / C++  
✅ Markdown  
✅ JSON / YAML  

*More coming soon!*

## 🤖 Supported LLM Providers

| Provider | Embeddings | Reranking | Cost | Status |
|----------|-----------|-----------|------|--------|
| **OpenAI** | text-embedding-3-large | gpt-4o-mini | $ | ✅ Ready |
| **Ollama** | nomic-embed-text | llama3.1 | FREE | ✅ Ready |
| Anthropic | voyage-3 | claude-3-haiku | $ | 🚧 Coming |
| Azure OpenAI | Same as OpenAI | Same as OpenAI | $ | 🚧 Coming |
| Google Vertex | text-embedding-004 | gemini-1.5-flash | $ | 🚧 Coming |
| Cohere | embed-english-v3 | command-r | $ | 🚧 Coming |

Choose your provider in `.editerra-racag.yaml`:

```yaml
llm_provider: "ollama"  # Free & local!

ollama:
  base_url: "http://localhost:11434"
  embedding_model: "nomic-embed-text"
  rerank_model: "llama3.1:8b"
```

## ⚙️ Configuration

Create `.editerra-racag.yaml` in your project root:

```yaml
# Project settings
project_name: "MyProject"
collection_name: "myproject_chunks"

# Paths
db_path: ".racag/db"
output_path: ".racag/output"

# LLM Provider
llm_provider: "openai"  # or "ollama", "anthropic", etc.

# OpenAI settings
openai:
  api_key: "${OPENAI_API_KEY}"
  embedding_model: "text-embedding-3-large"
  rerank_model: "gpt-4o-mini"

# Indexing
watch_enabled: true
exclude_dirs:
  - "node_modules"
  - ".git"
  - "build"
  - "dist"
```

## 📚 Documentation

- [Installation Guide](docs/installation.md) *(coming soon)*
- [Configuration Reference](docs/configuration.md) *(coming soon)*
- [LLM Provider Setup](docs/llm-providers.md) *(coming soon)*
- [Architecture Overview](docs/RACAG_STANDALONE_ANALYSIS.md)
- [API Reference](docs/api-reference.md) *(coming soon)*

## 🏗️ Project Status

**Current Status:** 🚧 Alpha Development

- [x] Core RACAG engine
- [x] Architecture design
- [x] Business Source License
- [ ] Multi-LLM provider abstraction
- [ ] Configuration system refactoring
- [ ] Python package (PyPI)
- [ ] VS Code extension
- [ ] MCP server
- [ ] Comprehensive documentation

**Target Launch:** Early January 2026

## 📈 Roadmap

### Phase 1 (Week 1) - Core Refactoring
- [ ] Dynamic configuration system
- [ ] Multi-LLM provider support (OpenAI, Ollama)
- [ ] Remove hardcoded paths

### Phase 2 (Week 2) - Python Package
- [ ] CLI interface
- [ ] PyPI publishing
- [ ] Tree-sitter grammar management

### Phase 3 (Week 3-4) - VS Code Extension
- [ ] Extension development
- [ ] Copilot integration
- [ ] Real-time indexing

### Phase 4 (Week 5) - MCP Server
- [ ] MCP protocol implementation
- [ ] Claude Desktop integration
- [ ] Testing with Cline/Continue.dev

### Phase 5 (Week 6) - Documentation & Launch
- [ ] Comprehensive docs
- [ ] Demo videos
- [ ] Marketing materials

## 💰 License & Pricing

**License:** Business Source License 1.1 (converts to Apache 2.0 after 3 years)

### Free Tier
✅ Individuals (unlimited)  
✅ Small teams (< 10 developers)  
✅ Open source projects  
✅ Educational use  

### Pro Tier ($19/user/month)
- Teams (10-100 developers)
- Priority support
- Private LLM integration
- Advanced analytics

### Enterprise (Custom)
- Unlimited developers
- White-label deployment
- On-premise installation
- SLA & dedicated support

[See full license details](LICENSE.md)

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. *(coming soon)*

**Areas we need help:**
- Additional LLM provider integrations
- More tree-sitter language grammars
- Documentation improvements
- Bug reports & feature requests

## 🙏 Acknowledgments

- Built on [ChromaDB](https://github.com/chroma-core/chroma) for vector storage
- Uses [tree-sitter](https://github.com/tree-sitter/tree-sitter) for code parsing
- Inspired by the need for better codebase understanding in AI tools

## 📧 Support & Contact

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/VSLinea/editerra-racag/issues)
- **Discussions:** [GitHub Discussions](https://github.com/VSLinea/editerra-racag/discussions)
- **Email:** support@editerra.io
- **Commercial Licensing:** licensing@editerra.io

## ⭐ Star Us!

If you find Editerra RAC-CAG useful, please give us a star! It helps others discover the project.

---

**Made with ❤️ by VSLinea**

*Editerra RAC-CAG - Making AI understand your code, not just read it.*
