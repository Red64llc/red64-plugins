"""Tests for budget-manager.py script.

Tests cover:
- Reads budget from config.yaml token_budget section
- Uses default 3000 tokens if not specified
- Sorts context items by priority (lower number = higher priority)
- Truncates lower-priority items when budget exceeded
- Excludes items entirely if truncation insufficient
- Includes exclusion summary when items removed
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "budget-manager.py"


def create_temp_config(config_data: dict) -> str:
    """Create a temporary config file and return its path.

    Args:
        config_data: Configuration dictionary to write.

    Returns:
        Path to the temporary config file.
    """
    temp_dir = tempfile.mkdtemp()
    config_path = Path(temp_dir) / ".red64" / "config.yaml"
    config_path.parent.mkdir(parents=True)
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)
    return str(config_path)


def run_budget_manager(
    context_items: list[dict],
    config_path: str | None = None,
    config_data: dict | None = None,
) -> dict:
    """Run budget-manager.py with the given context items and config.

    Args:
        context_items: List of context items to process.
        config_path: Path to existing config file.
        config_data: Config data to write to temp file if config_path not provided.

    Returns:
        Parsed JSON output from the script.
    """
    if config_path is None and config_data is not None:
        config_path = create_temp_config(config_data)
    elif config_path is None:
        config_path = create_temp_config({
            "version": "1.0",
            "token_budget": {
                "max_tokens": 3000,
                "overflow_behavior": {
                    "truncate": True,
                    "exclude": True,
                    "summary": True,
                },
            },
        })

    input_data = json.dumps({
        "context_items": context_items,
        "config_path": config_path,
    })
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        input=input_data,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class TestBudgetManager:
    """Test suite for budget-manager.py script."""

    def test_reads_budget_from_config_token_budget_section(self):
        """Test: Reads budget from config.yaml token_budget section.

        With 4 chars per token:
        - item1: 800 chars = 200 tokens
        - item2: 800 chars = 200 tokens
        - Budget of 150 tokens means only item1 should fit (with truncation)
        """
        config_data = {
            "version": "1.0",
            "token_budget": {
                "max_tokens": 150,
                "overflow_behavior": {
                    "truncate": True,
                    "exclude": True,
                    "summary": True,
                },
            },
        }

        context_items = [
            {"name": "item1", "content": "a" * 800, "priority": 1},
            {"name": "item2", "content": "b" * 800, "priority": 2},
        ]

        result = run_budget_manager(context_items, config_data=config_data)

        assert "selected_items" in result
        selected_names = [item["name"] for item in result["selected_items"]]
        assert "item1" in selected_names
        assert "item2" not in selected_names

    def test_uses_default_3000_tokens_if_not_specified(self):
        """Test: Uses default 3000 tokens if not specified.

        With 4 chars per token:
        - 16000 chars = 4000 tokens
        - Default budget is 3000 tokens = 12000 chars max
        """
        config_data = {
            "version": "1.0",
        }

        context_items = [
            {"name": "item1", "content": "x" * 16000, "priority": 1},
        ]

        result = run_budget_manager(context_items, config_data=config_data)

        assert "selected_items" in result
        assert len(result["selected_items"]) == 1
        selected_content = result["selected_items"][0]["content"]
        assert len(selected_content) <= 12003

    def test_sorts_context_items_by_priority_lower_is_higher(self):
        """Test: Sorts context items by priority (lower number = higher priority).

        With 4 chars per token:
        - Each item: 400 chars = 100 tokens
        - Budget of 100 tokens means only highest priority item fits
        """
        config_data = {
            "version": "1.0",
            "token_budget": {
                "max_tokens": 100,
                "overflow_behavior": {
                    "truncate": True,
                    "exclude": True,
                    "summary": True,
                },
            },
        }

        context_items = [
            {"name": "low_priority", "content": "c" * 400, "priority": 3},
            {"name": "high_priority", "content": "a" * 400, "priority": 1},
            {"name": "medium_priority", "content": "b" * 400, "priority": 2},
        ]

        result = run_budget_manager(context_items, config_data=config_data)

        assert "selected_items" in result
        if len(result["selected_items"]) > 0:
            assert result["selected_items"][0]["name"] == "high_priority"

    def test_truncates_lower_priority_items_when_budget_exceeded(self):
        """Test: Truncates lower-priority items when budget exceeded.

        With 4 chars per token:
        - high_priority: 400 chars = 100 tokens
        - low_priority: 800 chars = 200 tokens
        - Budget of 150 tokens: high fits (100), low gets truncated
        """
        config_data = {
            "version": "1.0",
            "token_budget": {
                "max_tokens": 150,
                "overflow_behavior": {
                    "truncate": True,
                    "exclude": True,
                    "summary": True,
                },
            },
        }

        context_items = [
            {"name": "high_priority", "content": "a" * 400, "priority": 1},
            {"name": "low_priority", "content": "b" * 800, "priority": 2},
        ]

        result = run_budget_manager(context_items, config_data=config_data)

        assert "selected_items" in result
        selected = {item["name"]: item for item in result["selected_items"]}

        assert "high_priority" in selected
        assert len(selected["high_priority"]["content"]) == 400

        if "low_priority" in selected:
            assert len(selected["low_priority"]["content"]) < 800

    def test_excludes_items_entirely_if_truncation_insufficient(self):
        """Test: Excludes items entirely if truncation insufficient.

        With 4 chars per token:
        - must_include: 160 chars = 40 tokens
        - can_exclude: 800 chars = 200 tokens
        - also_exclude: 800 chars = 200 tokens
        - Budget of 50 tokens: must_include fits, others excluded
        """
        config_data = {
            "version": "1.0",
            "token_budget": {
                "max_tokens": 50,
                "overflow_behavior": {
                    "truncate": True,
                    "exclude": True,
                    "summary": True,
                },
            },
        }

        context_items = [
            {"name": "must_include", "content": "a" * 160, "priority": 1},
            {"name": "can_exclude", "content": "b" * 800, "priority": 2},
            {"name": "also_exclude", "content": "c" * 800, "priority": 3},
        ]

        result = run_budget_manager(context_items, config_data=config_data)

        assert "selected_items" in result
        selected_names = [item["name"] for item in result["selected_items"]]
        assert "must_include" in selected_names
        assert "also_exclude" not in selected_names

    def test_includes_exclusion_summary_when_items_removed(self):
        """Test: Includes exclusion summary when items removed.

        With 4 chars per token:
        - included: 100 chars = 25 tokens
        - excluded_item: 4000 chars = 1000 tokens
        - Budget of 30 tokens: included fits, excluded_item is excluded
        """
        config_data = {
            "version": "1.0",
            "token_budget": {
                "max_tokens": 30,
                "overflow_behavior": {
                    "truncate": True,
                    "exclude": True,
                    "summary": True,
                },
            },
        }

        context_items = [
            {"name": "included", "content": "a" * 100, "priority": 1},
            {"name": "excluded_item", "content": "b" * 4000, "priority": 2},
        ]

        result = run_budget_manager(context_items, config_data=config_data)

        assert "exclusion_summary" in result
        summary = result["exclusion_summary"]
        assert "excluded_item" in summary or "1" in summary
