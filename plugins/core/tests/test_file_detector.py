"""Tests for file-detector.py script.

Tests cover:
- Detecting .py extension from prompt mentioning Python files
- Detecting .ts extension from prompt mentioning TypeScript files
- Detecting .md extension from prompt mentioning markdown files
- Detecting explicit filenames (e.g., "config.yaml", "hooks.json")
- Detecting path references (e.g., "plugins/core/scripts/")
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "file-detector.py"


def run_file_detector(prompt: str) -> dict:
    """Run file-detector.py with the given prompt.

    Args:
        prompt: The user prompt to analyze for file types.

    Returns:
        Parsed JSON output from the script.
    """
    input_data = json.dumps({"prompt": prompt})
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        input=input_data,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class TestFileDetector:
    """Test suite for file-detector.py script."""

    def test_detects_py_extension_from_prompt_mentioning_python_files(self):
        """Test: Detects .py extension from prompt mentioning Python files."""
        prompt = "Create a Python file that processes the data"
        result = run_file_detector(prompt)

        assert "file_types" in result
        assert ".py" in result["file_types"]

    def test_detects_ts_extension_from_prompt_mentioning_typescript_files(self):
        """Test: Detects .ts extension from prompt mentioning TypeScript files."""
        prompt = "Write a TypeScript function for the API"
        result = run_file_detector(prompt)

        assert "file_types" in result
        assert ".ts" in result["file_types"]

    def test_detects_md_extension_from_prompt_mentioning_markdown_files(self):
        """Test: Detects .md extension from prompt mentioning markdown files."""
        prompt = "Update the markdown documentation for the API"
        result = run_file_detector(prompt)

        assert "file_types" in result
        assert ".md" in result["file_types"]

    def test_detects_explicit_filenames(self):
        """Test: Detects explicit filenames (e.g., "config.yaml", "hooks.json")."""
        prompt = "Edit the config.yaml file and update hooks.json with new values"
        result = run_file_detector(prompt)

        assert "file_types" in result
        assert "config.yaml" in result["file_types"]
        assert "hooks.json" in result["file_types"]

    def test_detects_path_references(self):
        """Test: Detects path references (e.g., "plugins/core/scripts/")."""
        prompt = "Look at the files in plugins/core/scripts/ directory"
        result = run_file_detector(prompt)

        assert "file_types" in result
        assert "plugins/core/scripts/" in result["file_types"]
