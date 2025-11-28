"""Tests for context-loader.py main script.

Tests cover:
- Receives prompt via stdin JSON correctly
- Validates config presence and exits code 2 if missing
- Validates config format and exits code 2 if malformed
- Chains to task-detector.py and captures output
- Chains to file-detector.py and captures output
- Chains to budget-manager.py and captures output
- Returns valid JSON with hookSpecificOutput.additionalContext
- Error message directs user to run /red64:init if config missing
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "context-loader.py"


def create_temp_project(
    with_config: bool = True,
    config_data: dict | None = None,
    malformed_yaml: bool = False,
) -> str:
    """Create a temporary project directory with optional .red64/config.yaml.

    Args:
        with_config: Whether to create config.yaml.
        config_data: Custom config data (uses defaults if None).
        malformed_yaml: If True, write invalid YAML content.

    Returns:
        Path to the temporary project directory.
    """
    temp_dir = tempfile.mkdtemp()

    if with_config:
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir(parents=True)
        config_path = red64_dir / "config.yaml"

        if malformed_yaml:
            with open(config_path, "w") as f:
                f.write("invalid: yaml: content: [unclosed")
        else:
            if config_data is None:
                config_data = {
                    "version": "1.0",
                    "token_budget": {
                        "max_tokens": 3000,
                        "overflow_behavior": {
                            "truncate": True,
                            "exclude": True,
                            "summary": True,
                        },
                    },
                    "context_loader": {
                        "enabled": True,
                        "task_detection": True,
                        "file_type_detection": True,
                    },
                    "priorities": {
                        "product_mission": 1,
                        "current_spec": 2,
                        "relevant_standards": 3,
                        "tech_stack": 4,
                        "roadmap": 5,
                    },
                    "features": {
                        "standards_injection": False,
                        "multi_agent": False,
                        "metrics": False,
                    },
                }
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

    return temp_dir


def run_context_loader(
    prompt: str = "test prompt",
    session_id: str = "test-session",
    cwd: str | None = None,
    permission_mode: str = "default",
) -> tuple[dict | str, int]:
    """Run context-loader.py with the given input.

    Args:
        prompt: The user prompt.
        session_id: Session identifier.
        cwd: Current working directory.
        permission_mode: Permission mode setting.

    Returns:
        Tuple of (parsed output or raw stdout, exit code).
    """
    if cwd is None:
        cwd = os.getcwd()

    input_data = json.dumps({
        "session_id": session_id,
        "prompt": prompt,
        "cwd": cwd,
        "permission_mode": permission_mode,
    })

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        input=input_data,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SCRIPT_PATH.parent)},
    )

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = result.stdout

    return output, result.returncode


class TestContextLoader:
    """Test suite for context-loader.py main script."""

    def test_receives_prompt_via_stdin_json_correctly(self):
        """Test: Receives prompt via stdin JSON correctly.

        The script should accept JSON input with session_id, prompt, cwd,
        and permission_mode fields and process without error.
        """
        temp_dir = create_temp_project(with_config=True)

        output, exit_code = run_context_loader(
            prompt="Implement a new feature",
            session_id="session-123",
            cwd=temp_dir,
            permission_mode="default",
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        assert "hookSpecificOutput" in output

    def test_validates_config_presence_exits_code_2_if_missing(self):
        """Test: Validates config presence and exits code 2 if missing.

        When .red64/config.yaml does not exist, the script should exit
        with code 2 (blocking error).
        """
        temp_dir = create_temp_project(with_config=False)

        output, exit_code = run_context_loader(
            prompt="Implement a new feature",
            cwd=temp_dir,
        )

        assert exit_code == 2

    def test_validates_config_format_exits_code_2_if_malformed(self):
        """Test: Validates config format and exits code 2 if malformed.

        When config.yaml contains invalid YAML, the script should exit
        with code 2 (blocking error).
        """
        temp_dir = create_temp_project(with_config=True, malformed_yaml=True)

        output, exit_code = run_context_loader(
            prompt="Implement a new feature",
            cwd=temp_dir,
        )

        assert exit_code == 2

    def test_chains_to_task_detector_and_captures_output(self):
        """Test: Chains to task-detector.py and captures output.

        The context loader should invoke task-detector.py and include
        the detected task type in its output.
        """
        temp_dir = create_temp_project(with_config=True)

        output, exit_code = run_context_loader(
            prompt="Implement the user authentication feature",
            cwd=temp_dir,
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "implement" in additional_context.lower() or "task" in additional_context.lower()

    def test_chains_to_file_detector_and_captures_output(self):
        """Test: Chains to file-detector.py and captures output.

        The context loader should invoke file-detector.py and include
        detected file types in its output.
        """
        temp_dir = create_temp_project(with_config=True)

        output, exit_code = run_context_loader(
            prompt="Update the config.yaml and main.py files",
            cwd=temp_dir,
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert ".py" in additional_context or ".yaml" in additional_context or "file" in additional_context.lower()

    def test_chains_to_budget_manager_and_captures_output(self):
        """Test: Chains to budget-manager.py and captures output.

        The context loader should invoke budget-manager.py to manage
        token budget for context items.
        """
        temp_dir = create_temp_project(with_config=True)

        output, exit_code = run_context_loader(
            prompt="Review the codebase",
            cwd=temp_dir,
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        assert "hookSpecificOutput" in output

    def test_returns_valid_json_with_hook_specific_output(self):
        """Test: Returns valid JSON with hookSpecificOutput.additionalContext.

        The output must follow the Claude Code hook specification with
        the hookSpecificOutput.additionalContext structure.
        """
        temp_dir = create_temp_project(with_config=True)

        output, exit_code = run_context_loader(
            prompt="Debug the failing tests",
            cwd=temp_dir,
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        assert "hookSpecificOutput" in output
        assert "additionalContext" in output["hookSpecificOutput"]
        assert isinstance(output["hookSpecificOutput"]["additionalContext"], str)

    def test_error_message_directs_user_to_run_red64_init(self):
        """Test: Error message directs user to run /red64:init if config missing.

        When config is missing, the error message should include clear
        instructions to run /red64:init.
        """
        temp_dir = create_temp_project(with_config=False)

        output, exit_code = run_context_loader(
            prompt="Implement a new feature",
            cwd=temp_dir,
        )

        assert exit_code == 2
        assert isinstance(output, dict)
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "/red64:init" in additional_context
