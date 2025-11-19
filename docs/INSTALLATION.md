# Installation Guide - Editerra RAC-CAG

## Prerequisites

### Required
- **Python 3.9 or higher** ([Download Python](https://www.python.org/downloads/))
- **Git** (for cloning the repository)
- **Internet connection** (for downloading dependencies)

### Optional (depending on LLM provider)
- **OpenAI API Key** - If using OpenAI ($$$)
- **Ollama** - If using local/free models ([Download Ollama](https://ollama.ai))
- **Anthropic API Key** - If using Claude (coming soon)

---

## Installation Methods

### Method 1: Install from PyPI (Recommended - Coming Soon)

Once published to PyPI, installation will be:

```bash
# Install globally
pip install editerra-racag

# Or use pipx for isolated installation
pipx install editerra-racag
```

That's it! The `editerra-racag` command will be available globally.

---

### Method 2: Install from Source (Current Method)

**Step 1: Clone the repository**

```bash
git clone https://github.com/VSLinea/editerra-racag.git
cd editerra-racag
```

**Step 2: Create virtual environment (recommended)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Step 3: Install the package**

```bash
# Install in development mode (for contributors)
pip install -e ".[dev]"

# Or install for normal use
pip install .
```

**Step 4: Verify installation**

```bash
editerra-racag --version
editerra-racag providers
```

---

## Quick Start

### 1. Choose Your LLM Provider

#### Option A: OpenAI (Paid, Best Quality)

```bash
# Set your API key
export OPENAI_API_KEY="sk-your-key-here"

# Or add to ~/.zshrc or ~/.bashrc:
echo 'export OPENAI_API_KEY="sk-your-key-here"' >> ~/.zshrc
```

**Cost**: ~$0.01-0.05 per 1000 code chunks

#### Option B: Ollama (Free, Local)

```bash
# Install Ollama
# macOS:
brew install ollama

# Or download from https://ollama.ai

# Start Ollama service
ollama serve &

# Pull required models
ollama pull nomic-embed-text    # For embeddings (~270MB)
ollama pull llama3.1:8b         # For reranking (~4.7GB)
```

**Cost**: $0 (fully local)

---

### 2. Initialize in Your Project

```bash
# Navigate to your project
cd /path/to/your/project

# Initialize Editerra RAC-CAG
editerra-racag init --provider ollama
# Or: --provider openai

# This creates .editerra-racag.yaml
```

---

### 3. Index Your Codebase

```bash
# Build the vector database
editerra-racag index

# This will:
# - Scan your source files
# - Create semantic chunks
# - Generate embeddings
# - Store in local ChromaDB
```

---

### 4. Query Your Code

```bash
# Search your codebase
editerra-racag query "Where is authentication handled?"

# With more results
editerra-racag query "How does the API routing work?" --top-k 10
```

---

## What Gets Installed?

### Python Dependencies

When you run `pip install editerra-racag`, these packages are automatically installed:

#### Core Dependencies
```
chromadb==0.4.24          # Vector database (pinned: 1.3.5+ has segfault issues)
openai>=1.0.0             # OpenAI API client
tiktoken>=0.5.0           # Token counting
fastapi>=0.104.0          # API framework
uvicorn>=0.24.0           # ASGI server
pydantic>=2.0.0           # Data validation
python-dotenv>=1.0.0      # Environment variables
PyYAML>=6.0               # Configuration files
tree-sitter>=0.20.0       # Code parsing
watchdog>=3.0.0           # File watching
click>=8.0.0              # CLI framework
rich>=13.0.0              # Terminal formatting
numpy>=1.23.0,<2.0.0      # Array operations (NumPy 2.0 breaks ChromaDB 0.4.x)
```

#### Optional Dependencies
```
# For Ollama support
pip install editerra-racag[ollama]

# For Anthropic/Claude support (coming soon)
pip install editerra-racag[anthropic]

# For all providers
pip install editerra-racag[all]
```

### What Gets Created on Your Machine?

```
Your Project/
├── .editerra-racag.yaml       # Configuration file
└── .editerra-racag/           # Data directory
    ├── db/                    # Vector database (SQLite)
    │   └── chroma.sqlite3     # ~10-100MB depending on project size
    ├── output/                # Intermediate files
    │   ├── chunks.jsonl       # Extracted code chunks
    │   └── meta_summary.json  # Index statistics
    └── cache/                 # Embedding cache (optional)
```

**Storage Requirements**:
- Small project (< 1,000 files): ~50MB
- Medium project (1,000-10,000 files): ~200-500MB
- Large project (> 10,000 files): ~1GB+

---

## Platform-Specific Notes

### macOS
```bash
# Install Python via Homebrew
brew install python@3.11

# Install with pip
pip3 install editerra-racag
```

### Linux (Ubuntu/Debian)
```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install with pip
pip3 install editerra-racag
```

### Windows
```powershell
# Install Python from python.org
# Then install with pip
pip install editerra-racag

# Or use Windows Subsystem for Linux (WSL)
```

---

## Deployment Scenarios

### Scenario 1: Individual Developer (Simplest)

```bash
# One-time setup
pip install editerra-racag
export OPENAI_API_KEY="sk-..."

# Per project
cd my-project
editerra-racag init
editerra-racag index
```

### Scenario 2: Team Environment

```bash
# Each team member does:
git clone https://github.com/company/project.git
cd project

# .editerra-racag.yaml is already in git
# Just install and index
pip install editerra-racag
editerra-racag index
```

**Note**: Add `.editerra-racag/` to `.gitignore` (database is local)

### Scenario 3: CI/CD Pipeline

```yaml
# .github/workflows/index.yml
name: Index Codebase
on: [push]
jobs:
  index:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install editerra-racag
      - run: editerra-racag index
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### Scenario 4: Docker Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install Editerra RAC-CAG
RUN pip install editerra-racag

# Copy project
COPY . /app
WORKDIR /app

# Index on build
RUN editerra-racag index

# Serve API
CMD ["editerra-racag", "serve", "--port", "8009"]
```

---

## VS Code Extension (Coming Soon)

For the smoothest experience, install the VS Code extension:

1. Open VS Code
2. Go to Extensions (⌘+Shift+X)
3. Search for "Editerra RAC-CAG"
4. Click Install

The extension will:
- ✅ Auto-detect Python installation
- ✅ Prompt to install `editerra-racag` package
- ✅ Guide you through API key setup
- ✅ Index workspace automatically
- ✅ Integrate with GitHub Copilot

---

## MCP Server (for Claude Desktop)

### Installation

```bash
# Install MCP server (comes with package)
pip install editerra-racag
```

### Configuration

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "editerra-racag": {
      "command": "editerra-racag-mcp",
      "args": ["--workspace", "/path/to/your/project"],
      "env": {
        "OPENAI_API_KEY": "sk-your-key-here"
      }
    }
  }
}
```

Restart Claude Desktop, and you'll have the `query_codebase` tool!

---

## Troubleshooting

### "Command not found: editerra-racag"

**Solution 1**: Ensure pip bin directory is in PATH
```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
```

**Solution 2**: Use `python -m` syntax
```bash
python3 -m editerra_racag.cli --help
```

### "OpenAI API key not configured"

```bash
# Set environment variable
export OPENAI_API_KEY="sk-your-actual-key"

# Or add to .editerra-racag.yaml
openai:
  api_key: "sk-your-actual-key"
```

### "Cannot connect to Ollama"

```bash
# Start Ollama service
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### "ChromaDB errors" or Segfault/Crash

**Issue**: ChromaDB 1.3.5+ has known segfault issues with concurrent operations.

**Solution**: We pin to ChromaDB 0.4.24 which is stable. If you still see issues:

```bash
# Ensure correct versions are installed
pip install "chromadb==0.4.24" "numpy<2.0.0"

# Clear database and rebuild
rm -rf .editerra-racag/db/
editerra-racag index
```

**Note**: NumPy 2.0 has breaking changes incompatible with ChromaDB 0.4.x. We explicitly require NumPy <2.0.0.

---

## Upgrading

### From PyPI
```bash
pip install --upgrade editerra-racag
```

### From Source
```bash
cd editerra-racag
git pull
pip install -e ".[dev]"
```

---

## Uninstalling

```bash
# Remove package
pip uninstall editerra-racag

# Remove project data
rm -rf .editerra-racag/

# Remove global config (optional)
rm -rf ~/.editerra-racag/
```

---

## System Requirements

### Minimum
- **CPU**: Dual-core processor
- **RAM**: 4GB
- **Storage**: 1GB free space
- **Python**: 3.9+

### Recommended
- **CPU**: Quad-core processor or better
- **RAM**: 8GB+ (16GB for large codebases)
- **Storage**: 5GB+ free space
- **Python**: 3.11+

### For Ollama (Local Mode)
- **RAM**: 16GB+ (models run in memory)
- **Storage**: 10GB+ (for model files)

---

## Next Steps

1. **Read the Quick Start**: See "Quick Start" section above
2. **Configure Your Provider**: Choose OpenAI or Ollama
3. **Index Your First Project**: `editerra-racag init && editerra-racag index`
4. **Try a Query**: `editerra-racag query "your question"`
5. **Integrate with Your Workflow**: VS Code extension or MCP server

---

## Getting Help

- **Documentation**: [docs/](../docs/)
- **Issues**: [GitHub Issues](https://github.com/VSLinea/editerra-racag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/VSLinea/editerra-racag/discussions)
- **Email**: support@editerra.io

---

**License**: Business Source License 1.1 (BSL)
- Free for individuals and small teams (< 10 developers)
- Commercial license required for larger organizations
- Converts to Apache 2.0 after 3 years

See [LICENSE.md](../LICENSE.md) for details.
