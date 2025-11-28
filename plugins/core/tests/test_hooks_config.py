"""Tests for hooks.json configuration.

Tests cover:
- Valid JSON matching Claude Code hook schema
- Correct script path reference
- Timeout configuration
"""

import json
from pathlib import Path

import pytest


HOOKS_FILE_PATH = Path(__file__).parent.parent / "hooks" / "hooks.json"
EXPECTED_SCRIPT_PATH = "python3 plugins/core/scripts/context-loader.py"
EXPECTED_TIMEOUT = 30


class TestHooksConfig:
    """Test suite for hooks.json configuration."""

    @pytest.fixture
    def hooks_config(self) -> dict:
        """Load and return the hooks.json configuration."""
        with open(HOOKS_FILE_PATH) as f:
            return json.load(f)

    def test_hooks_json_is_valid_json_matching_claude_code_schema(
        self, hooks_config: dict
    ):
        """Test: hooks.json is valid JSON matching Claude Code hook schema."""
        assert "hooks" in hooks_config
        assert "UserPromptSubmit" in hooks_config["hooks"]

        user_prompt_submit = hooks_config["hooks"]["UserPromptSubmit"]
        assert isinstance(user_prompt_submit, list)
        assert len(user_prompt_submit) > 0

        hook_group = user_prompt_submit[0]
        assert "hooks" in hook_group
        assert isinstance(hook_group["hooks"], list)
        assert len(hook_group["hooks"]) > 0

        hook = hook_group["hooks"][0]
        assert "type" in hook
        assert hook["type"] == "command"
        assert "command" in hook
        assert "timeout" in hook

    def test_hook_correctly_references_context_loader_script_path(
        self, hooks_config: dict
    ):
        """Test: Hook correctly references context-loader.py script path."""
        hook = hooks_config["hooks"]["UserPromptSubmit"][0]["hooks"][0]

        assert hook["command"] == EXPECTED_SCRIPT_PATH
        assert "context-loader.py" in hook["command"]
        assert "plugins/core/scripts/" in hook["command"]

    def test_timeout_is_configured_to_30_seconds(self, hooks_config: dict):
        """Test: Timeout is configured to 30 seconds."""
        hook = hooks_config["hooks"]["UserPromptSubmit"][0]["hooks"][0]

        assert hook["timeout"] == EXPECTED_TIMEOUT
