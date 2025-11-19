"""
Editerra RAC-CAG CLI
===================

Command-line interface for Editerra RAC-CAG.
"""

import click
from pathlib import Path
import sys
import json

from editerra_racag import __version__
from editerra_racag.config import init_config, get_config
from editerra_racag.engine import EditerraEngine
from editerra_racag.llm.factory import get_available_providers


@click.group()
@click.version_option(version=__version__, prog_name="editerra-racag")
def cli():
    """
    Editerra RAC-CAG - AI-Powered Code Intelligence
    
    Index your codebase and enable smart AI-assisted development.
    """
    pass


@cli.command()
@click.option(
    "--workspace",
    "-w",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Workspace directory (default: current directory)"
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "ollama", "anthropic", "azure"], case_sensitive=False),
    default="openai",
    help="LLM provider to use"
)
def init(workspace: Path, provider: str):
    """
    Initialize Editerra RAC-CAG in a workspace.
    
    Creates .editerra-racag.yaml configuration file.
    """
    click.echo(f"🚀 Initializing Editerra RAC-CAG in {workspace}")
    click.echo()
    
    try:
        config = init_config(workspace)
        
        # Set provider
        config.config["llm_provider"] = provider.lower()
        config.save()
        
        click.echo(f"✅ Created: {config.config_file}")
        click.echo(f"📦 LLM Provider: {provider}")
        click.echo()
        click.echo("Next steps:")
        click.echo("  1. Edit .editerra-racag.yaml if needed")
        
        if provider.lower() == "openai":
            click.echo("  2. Set OPENAI_API_KEY environment variable")
        elif provider.lower() == "ollama":
            click.echo("  2. Install Ollama from https://ollama.ai")
            click.echo("  3. Run: ollama pull nomic-embed-text && ollama pull llama3.1:8b")
        
        click.echo(f"  4. Run: editerra-racag index")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--workspace",
    "-w",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Workspace directory"
)
def index(workspace: Path):
    """
    Index the workspace (chunking + embedding).
    
    Scans all source files, creates chunks, and builds the vector database.
    """
    click.echo(f"📊 Indexing workspace: {workspace}")
    click.echo()
    
    try:
        config = get_config(workspace)
        click.echo(f"📝 Project: {config.project_name}")
        click.echo(f"🤖 Provider: {config.llm_provider}")
        click.echo(f"💾 Database: {config.db_path}")
        click.echo()
        
        # Initialize engine
        engine = EditerraEngine(workspace, config)
        
        # Run indexing
        click.echo("⚙️  Starting indexing pipeline...")
        stats = engine.index()
        
        # Display results
        click.echo()
        click.echo("✅ Indexing complete!")
        click.echo()
        click.echo(f"📦 Total chunks: {stats.get('chunking', {}).get('total_chunks', 0)}")
        click.echo(f"🔢 Total embeddings: {stats.get('embedding', {}).get('total_embedded', 0)}")
        click.echo(f"💾 Collection: {stats['collection']}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("query_text", nargs=-1, required=True)
@click.option(
    "--workspace",
    "-w",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Workspace directory"
)
@click.option(
    "--top-k",
    "-k",
    type=int,
    default=5,
    help="Number of results to return"
)
def query(query_text, workspace: Path, top_k: int):
    """
    Query the codebase.
    
    Search for relevant code snippets using natural language.
    """
    query_str = " ".join(query_text)
    
    click.echo(f"🔍 Query: {query_str}")
    click.echo()
    
    try:
        config = get_config(workspace)
        engine = EditerraEngine(workspace, config)
        
        # Execute query
        results = engine.query(query_str, top_k=top_k)
        
        if not results:
            click.echo("❌ No results found")
            return
        
        # Display results
        click.echo(f"✅ Found {len(results)} relevant chunks:")
        click.echo()
        
        for i, result in enumerate(results, 1):
            click.echo(f"─── Result {i} ───")
            click.echo(f"📄 File: {result.get('file_path', 'Unknown')}")
            click.echo(f"📍 Lines: {result.get('start_line', '?')}-{result.get('end_line', '?')}")
            click.echo(f"🎯 Score: {result.get('score', 0):.3f}")
            click.echo()
            click.echo(result.get('content', ''))
            click.echo()
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    "--workspace",
    "-w",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Workspace directory"
)
def stats(workspace: Path):
    """
    Show index statistics.
    
    Displays information about the current index.
    """
    click.echo(f"📈 Index Statistics for: {workspace}")
    click.echo()
    
    try:
        config = get_config(workspace)
        engine = EditerraEngine(workspace, config)
        
        stats = engine.get_stats()
        
        click.echo(f"📝 Project: {config.project_name}")
        click.echo(f"📦 Collection: {stats['collection']}")
        click.echo(f"🤖 Provider: {stats['provider']}")
        click.echo(f"💾 Database: {stats['db_path']}")
        click.echo(f"🔢 Total chunks: {stats.get('total_chunks', 0)}")
        click.echo()
        
        if 'last_index' in stats:
            last = stats['last_index']
            click.echo("Last indexing:")
            chunk_stats = last.get('chunking', {})
            embed_stats = last.get('embedding', {})
            click.echo(f"  • Chunks created: {chunk_stats.get('total_chunks', 0)}")
            click.echo(f"  • Embeddings: {embed_stats.get('total_embedded', 0)}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--workspace",
    "-w",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Workspace directory"
)
def watch(workspace: Path):
    """
    Watch for file changes and update index incrementally.
    """
    click.echo(f"👀 Watching workspace: {workspace}")
    click.echo("Press Ctrl+C to stop")
    click.echo()
    
    try:
        config = get_config(workspace)
        
        from editerra_racag.watcher.file_watcher import FileWatcher
        
        # Initialize watcher
        watcher = FileWatcher(
            workspace_root=str(workspace),
            config=config
        )
        
        click.echo(f"✅ Watcher initialized")
        click.echo(f"📁 Monitoring: {workspace}")
        click.echo()
        
        # Start watching
        watcher.start()
        
    except KeyboardInterrupt:
        click.echo("\n⏹️  Stopping watcher...")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    "--workspace",
    "-w",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd(),
    help="Workspace directory"
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=8009,
    help="Port to run server on"
)
def serve(workspace: Path, port: int):
    """
    Start the API server.
    
    Launches FastAPI server for HTTP access.
    """
    click.echo(f"🌐 Starting API server on port {port}")
    click.echo(f"📁 Workspace: {workspace}")
    click.echo()
    
    try:
        import uvicorn
        from editerra_racag.api.server import create_app
        
        # Create FastAPI app with workspace context
        app = create_app(workspace)
        
        click.echo(f"✅ Server starting...")
        click.echo(f"📍 URL: http://localhost:{port}")
        click.echo(f"📄 Docs: http://localhost:{port}/docs")
        click.echo()
        
        # Start server
        uvicorn.run(app, host="0.0.0.0", port=port)
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
def providers():
    """
    List available LLM providers and their status.
    """
    click.echo("🤖 Available LLM Providers:")
    click.echo()
    
    # Get dynamically available providers
    available = get_available_providers()
    
    providers_list = [
        ("openai", "OpenAI", "✅ Ready" if "openai" in available else "❌ Not available", "Requires API key"),
        ("ollama", "Ollama (Local)", "✅ Ready" if "ollama" in available else "❌ Not available", "Free, requires Ollama installation"),
        ("anthropic", "Anthropic Claude", "🚧 Coming Soon", "Requires API key"),
        ("azure", "Azure OpenAI", "🚧 Coming Soon", "Enterprise"),
        ("vertex", "Google Vertex AI", "🚧 Coming Soon", "Requires GCP"),
        ("cohere", "Cohere", "🚧 Coming Soon", "Requires API key"),
    ]
    
    for key, name, status, note in providers_list:
        click.echo(f"  {status} {name:25} ({key})")
        click.echo(f"       → {note}")
        click.echo()


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
