#!/usr/bin/env -S venv/bin/python
import argparse
import sys
import logging
from typing import List
from pathlib import Path
from config import (
    DATA_DIR, PROFILE_FILE, RECOMMENDATIONS_FILE,
    HISTORY_FILE, CANDIDATES_FILE
)

# Import from core package
from core import fetch_data
from core import recommend
from core import profile_taste
from core import mark_watched

# Setup logger
logger = logging.getLogger(__name__)

def setup_logging(verbose: bool):
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

def load_items_from_file(file_path: str) -> List[str]:
    """Load items from a text file, one per line."""
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return []
        
    try:
        with open(path, "r") as f:
            items = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(items)} items from {file_path}")
        return items
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return []

def handle_fetch(args):
    """Fetch watch history and candidates."""
    logger.info("Starting data fetch...")
    fetch_data.main()

def handle_profile(args):
    """Generate taste profile."""
    logger.info("Generating taste profile...")
    profile_taste.main()

def handle_recommend(args):
    """Generate recommendations."""
    logger.info("Generating recommendations...")
    
    seed_items = []
    
    # Add CLI args
    if args.items:
        seed_items.extend(args.items)
        
    # Add file args
    if args.file:
        seed_items.extend(load_items_from_file(args.file))
        
    recommend.main(seed_items=seed_items)


def handle_mark(args):
    """Mark items as watched."""
    unique_items = set()
    
    # Add CLI args
    if args.items:
        unique_items.update(args.items)
        
    # Add file args
    if args.file:
        unique_items.update(load_items_from_file(args.file))
    
    if not unique_items:
        logger.error("No items specified to mark as watched. Use arguments or --file.")
        return
    
    # Convert back to list for processing
    items_list = list(unique_items)
    mark_watched.process_titles(items_list)

def main():
    parser = argparse.ArgumentParser(description="Trakt Agent CLI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Fetch Command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch watch history and candidates")
    
    # Profile Command
    profile_parser = subparsers.add_parser("profile", help="Generate taste profile analysis")
    
    # Recommend Command
    recommend_parser = subparsers.add_parser("recommend", help="Generate content recommendations")
    recommend_parser.add_argument("items", nargs="*", help="Optional list of seed titles for recommendations")
    recommend_parser.add_argument("-f", "--file", help="Path to file containing seed titles (one per line)")
    
    # Mark Command
    mark_parser = subparsers.add_parser("mark", help="Mark items as watched (by title)")
    mark_parser.add_argument("items", nargs="*", help="List of titles to mark as watched")
    mark_parser.add_argument("-f", "--file", help="Path to file containing titles to mark (one per line)")

    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if args.command == "fetch":
        handle_fetch(args)
    elif args.command == "profile":
        handle_profile(args)
    elif args.command == "recommend":
        handle_recommend(args)
    elif args.command == "mark":
        handle_mark(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
