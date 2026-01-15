#!/bin/bash
# Integrated workflow script for updating recommendations
# Usage: ./update_recommendations.sh "Movie 1" "Movie 2" "TV Show 1" ...

set -e  # Exit on error

# Use virtual environment Python
PYTHON="./venv/bin/python"

echo "=========================================="
echo "Trakt Recommendation Update Workflow"
echo "=========================================="
echo ""

if [ $# -eq 0 ]; then
    echo "Usage: $0 'Title 1' 'Title 2' ..."
    echo "Example: $0 'Inception' 'The Matrix' 'Breaking Bad'"
    exit 1
fi

# Step 1: Mark items as watched
echo "Step 1/4: Marking items as watched..."
$PYTHON search_and_mark.py "$@"
echo ""

# Step 2: Fetch latest data from Trakt
echo "Step 2/4: Fetching latest data from Trakt..."
$PYTHON fetch_data.py
echo ""

# Step 3: Generate recommendations
echo "Step 3/4: Generating new recommendations..."
$PYTHON recommend.py
echo ""

# Step 4: Done!
echo "=========================================="
echo "✅ Workflow Complete!"
echo "=========================================="
echo "Check your Obsidian vault for new recommendations:"
echo "  → Trakt Recommendations.md"
echo ""
