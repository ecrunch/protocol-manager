"""
Main entry point for running the Notion client as a module.

Allows usage like: python -m notion_client <command>
"""

from .cli import main

if __name__ == "__main__":
    main()
