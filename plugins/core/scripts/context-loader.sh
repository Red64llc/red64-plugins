#!/bin/bash
# Portable wrapper for context-loader.py
# Uses dirname to find the script location regardless of cwd
# Works from any working directory

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Ensure Python can find our modules
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

exec python3 "$SCRIPT_DIR/context-loader.py" "$@"
