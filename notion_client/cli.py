"""
Command-line interface for the Notion Python client.

This module provides a simple CLI for basic Notion operations and testing.
"""

import sys
import os
from typing import Optional

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False

from .client import NotionClient
from .exceptions import NotionAPIError


def print_error(message: str) -> None:
    """Print error message to stderr."""
    print(f"Error: {message}", file=sys.stderr)


def simple_cli() -> None:
    """Simple CLI without click dependency."""
    if len(sys.argv) < 2:
        print("Usage: python -m notion_client.cli <command>")
        print("Commands:")
        print("  test-connection  - Test connection to Notion API")
        print("  workspace-info   - Get workspace information")
        print("  search <query>   - Search for pages and databases")
        return

    command = sys.argv[1]
    
    try:
        client = NotionClient.from_env()
    except Exception as e:
        print_error(f"Failed to initialize client: {e}")
        print("Make sure NOTION_API_TOKEN is set in your environment or .env file")
        return

    try:
        if command == "test-connection":
            if client.test_connection():
                print("✅ Connected to Notion API successfully!")
            else:
                print("❌ Failed to connect to Notion API")
        
        elif command == "workspace-info":
            info = client.get_workspace_info()
            print("📋 Workspace Information:")
            print(f"   Bot User: {info.get('bot_user', {}).get('name', 'Unknown')}")
            print(f"   Workspace: {info.get('workspace_name', 'Unknown')}")
            print(f"   API Version: {info.get('api_version', 'Unknown')}")
            print(f"   Status: {info.get('connection_status', 'Unknown')}")
        
        elif command == "search":
            if len(sys.argv) < 3:
                print_error("Search command requires a query")
                return
            
            query = " ".join(sys.argv[2:])
            print(f"🔍 Searching for: {query}")
            
            results = client.search.search_all(query=query, page_size=10)
            
            if not results:
                print("No results found")
                return
            
            print(f"Found {len(results)} results:")
            for i, item in enumerate(results, 1):
                item_type = item.__class__.__name__
                
                # Get title
                if hasattr(item, 'title') and item.title:
                    # Database
                    title = "".join([t.plain_text for t in item.title])
                elif hasattr(item, 'properties') and item.properties:
                    # Page
                    title_prop = item.properties.get('title') or item.properties.get('Name')
                    if title_prop and title_prop.get('title'):
                        title = "".join([t.get('plain_text', '') for t in title_prop['title']])
                    else:
                        title = "Untitled"
                else:
                    title = "Unknown"
                
                print(f"  {i}. [{item_type}] {title}")
                print(f"     ID: {item.id}")
                if hasattr(item, 'url'):
                    print(f"     URL: {item.url}")
                print()
        
        else:
            print_error(f"Unknown command: {command}")
    
    except NotionAPIError as e:
        print_error(f"Notion API error: {e.message}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")


if HAS_CLICK:
    @click.group()
    @click.option('--token', envvar='NOTION_API_TOKEN', help='Notion API token')
    @click.pass_context
    def cli(ctx: click.Context, token: Optional[str]) -> None:
        """Notion Python Client CLI."""
        ctx.ensure_object(dict)
        
        try:
            if token:
                ctx.obj['client'] = NotionClient(auth_token=token)
            else:
                ctx.obj['client'] = NotionClient.from_env()
        except Exception as e:
            click.echo(f"Error: Failed to initialize client: {e}", err=True)
            ctx.exit(1)

    @cli.command()
    @click.pass_context
    def test_connection(ctx: click.Context) -> None:
        """Test connection to Notion API."""
        client = ctx.obj['client']
        
        if client.test_connection():
            click.echo("✅ Connected to Notion API successfully!")
        else:
            click.echo("❌ Failed to connect to Notion API", err=True)

    @cli.command()
    @click.pass_context
    def workspace_info(ctx: click.Context) -> None:
        """Get workspace information."""
        client = ctx.obj['client']
        
        try:
            info = client.get_workspace_info()
            click.echo("📋 Workspace Information:")
            click.echo(f"   Bot User: {info.get('bot_user', {}).get('name', 'Unknown')}")
            click.echo(f"   Workspace: {info.get('workspace_name', 'Unknown')}")
            click.echo(f"   API Version: {info.get('api_version', 'Unknown')}")
            click.echo(f"   Status: {info.get('connection_status', 'Unknown')}")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    @cli.command()
    @click.argument('query')
    @click.option('--limit', default=10, help='Maximum number of results')
    @click.pass_context
    def search(ctx: click.Context, query: str, limit: int) -> None:
        """Search for pages and databases."""
        client = ctx.obj['client']
        
        try:
            click.echo(f"🔍 Searching for: {query}")
            results = client.search.search_all(query=query, page_size=limit)
            
            if not results:
                click.echo("No results found")
                return
            
            click.echo(f"Found {len(results)} results:")
            
            for i, item in enumerate(results, 1):
                item_type = item.__class__.__name__
                
                # Get title
                if hasattr(item, 'title') and item.title:
                    title = "".join([t.plain_text for t in item.title])
                elif hasattr(item, 'properties') and item.properties:
                    title_prop = item.properties.get('title') or item.properties.get('Name')
                    if title_prop and title_prop.get('title'):
                        title = "".join([t.get('plain_text', '') for t in title_prop['title']])
                    else:
                        title = "Untitled"
                else:
                    title = "Unknown"
                
                click.echo(f"  {i}. [{item_type}] {title}")
                click.echo(f"     ID: {item.id}")
                if hasattr(item, 'url'):
                    click.echo(f"     URL: {item.url}")
                click.echo()
        
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


def main() -> None:
    """Main entry point for CLI."""
    if HAS_CLICK:
        cli()
    else:
        simple_cli()


if __name__ == "__main__":
    main()
