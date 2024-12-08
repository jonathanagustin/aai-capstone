#!/usr/bin/env bash
set -euo pipefail

# Check if inotifywait is installed
if ! command -v inotifywait >/dev/null 2>&1; then
    echo "inotifywait not found. Please install inotify-tools:"
    echo "  sudo apt-get install inotify-tools"
    exit 1
fi

echo "Starting development mode..."
echo "Watching for changes in content/*.yml and src/aai_capstone/*.py"
echo "Press Ctrl+C to stop."

while true; do
    # Wait for changes in content/*.yml or src/aai_capstone/*.py
    if inotifywait -q -e modify,create,delete content/*.yml src/aai_capstone/*.py 2>/dev/null; then
        echo -e "\nChange detected, regenerating..."
        task generate || echo "Generation failed; check logs."
    else
        echo "inotifywait encountered an error or was stopped."
        exit 1
    fi
done
