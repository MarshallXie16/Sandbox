#!/usr/bin/env python3
"""
Entry point for the sync CLI.

Usage:
    python sync_cli.py sync-all --direction bidirectional
    python sync_cli.py sync-contacts --dry-run
    python sync_cli.py show-mappings
"""

from app.cli.main import app

if __name__ == "__main__":
    app()
