"""Tests for task-detector.py script.

Tests cover:
- Detection of shape task from keywords
- Detection of implement task from keywords
- Detection of review task from keywords
- Detection of test task from keywords
- Detection of debug task from keywords
- Returns unknown for prompts with no matching keywords
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "task-detector.py"


def run_task_detector(prompt: str) -> dict:
    """Run the task detector script with given prompt.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        The parsed JSON output from the script.
    """
    input_data = json.dumps({"prompt": prompt})
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        input=input_data,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class TestTaskDetector:
    """Test suite for task-detector.py script."""

    def test_detects_shape_task_from_keywords(self):
        """Test: Detects shape task from keywords (requirements, scope, define)."""
        prompts = [
            "What are the requirements for this feature?",
            "Define the scope of this project",
            "Let's scope out the work needed",
        ]

        for prompt in prompts:
            output = run_task_detector(prompt)
            assert output["task_type"] == "shape", f"Failed for prompt: {prompt}"

    def test_detects_implement_task_from_keywords(self):
        """Test: Detects implement task from keywords (implement, build, create)."""
        prompts = [
            "Implement the user authentication feature",
            "Build a REST API endpoint",
            "Create a new component for the dashboard",
        ]

        for prompt in prompts:
            output = run_task_detector(prompt)
            assert output["task_type"] == "implement", f"Failed for prompt: {prompt}"

    def test_detects_review_task_from_keywords(self):
        """Test: Detects review task from keywords (review, check, audit)."""
        prompts = [
            "Review this pull request",
            "Check the code for quality",
            "Audit the security of this module",
        ]

        for prompt in prompts:
            output = run_task_detector(prompt)
            assert output["task_type"] == "review", f"Failed for prompt: {prompt}"

    def test_detects_test_task_from_keywords(self):
        """Test: Detects test task from keywords (test, verify, validate)."""
        prompts = [
            "Write tests for the user service",
            "Verify this function works correctly",
            "Validate the input data format",
        ]

        for prompt in prompts:
            output = run_task_detector(prompt)
            assert output["task_type"] == "test", f"Failed for prompt: {prompt}"

    def test_detects_debug_task_from_keywords(self):
        """Test: Detects debug task from keywords (debug, fix, error, bug)."""
        prompts = [
            "Debug this failing test",
            "Fix the login issue",
            "There's an error in the output",
            "This bug is causing crashes",
        ]

        for prompt in prompts:
            output = run_task_detector(prompt)
            assert output["task_type"] == "debug", f"Failed for prompt: {prompt}"

    def test_returns_unknown_for_no_matching_keywords(self):
        """Test: Returns unknown for prompts with no matching keywords."""
        prompts = [
            "Hello there",
            "What is the weather today?",
            "Tell me about Python",
        ]

        for prompt in prompts:
            output = run_task_detector(prompt)
            assert output["task_type"] == "unknown", f"Failed for prompt: {prompt}"
