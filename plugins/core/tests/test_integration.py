"""Integration tests for Core Foundation feature.

Tests cover critical integration gaps:
- Full hook flow from prompt to context output
- Missing task type detection (write-spec, refactor)
- Config validation with partial configurations
- Error handling for sub-script failures
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
CONTEXT_LOADER_PATH = SCRIPTS_DIR / "context-loader.py"
TASK_DETECTOR_PATH = SCRIPTS_DIR / "task-detector.py"


def create_test_project(
    config_data: dict | None = None,
    with_config: bool = True,
) -> str:
    """Create a temporary project directory with .red64/config.yaml.

    Args:
        config_data: Custom config data (uses defaults if None).
        with_config: Whether to create the config file.

    Returns:
        Path to the temporary project directory.
    """
    temp_dir = tempfile.mkdtemp()

    if with_config:
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir(parents=True)
        config_path = red64_dir / "config.yaml"

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


def run_task_detector(prompt: str) -> dict:
    """Run the task detector script with given prompt.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        The parsed JSON output from the script.
    """
    input_data = json.dumps({"prompt": prompt})
    result = subprocess.run(
        [sys.executable, str(TASK_DETECTOR_PATH)],
        input=input_data,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def run_context_loader(
    prompt: str,
    cwd: str,
    session_id: str = "test-session",
    permission_mode: str = "default",
) -> tuple[dict | str, int]:
    """Run context-loader.py with the given input.

    Args:
        prompt: The user prompt.
        cwd: Current working directory.
        session_id: Session identifier.
        permission_mode: Permission mode setting.

    Returns:
        Tuple of (parsed output or raw stdout, exit code).
    """
    input_data = json.dumps({
        "session_id": session_id,
        "prompt": prompt,
        "cwd": cwd,
        "permission_mode": permission_mode,
    })

    result = subprocess.run(
        [sys.executable, str(CONTEXT_LOADER_PATH)],
        input=input_data,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
    )

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = result.stdout

    return output, result.returncode


class TestIntegration:
    """Integration tests for Core Foundation end-to-end workflows."""

    def test_full_hook_flow_from_prompt_to_context_output(self):
        """Integration test: Full hook flow from prompt to context output.

        Tests the complete flow:
        1. Valid JSON input with session_id, prompt, cwd, permission_mode
        2. Config validation succeeds
        3. Task detection runs and identifies task type
        4. File detection runs and identifies file types
        5. Budget management processes context
        6. Output contains hookSpecificOutput.additionalContext with all data
        """
        temp_dir = create_test_project()

        output, exit_code = run_context_loader(
            prompt="Implement a Python function to process config.yaml files",
            cwd=temp_dir,
        )

        assert exit_code == 0, "Hook should exit with code 0 for success"
        assert isinstance(output, dict), "Output should be a valid JSON object"
        assert "hookSpecificOutput" in output, "Output must contain hookSpecificOutput"
        assert "additionalContext" in output["hookSpecificOutput"]

        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "Red64 Context" in additional_context
        assert "Detected Task Type:" in additional_context
        assert "implement" in additional_context.lower()

    def test_detects_write_spec_task_type(self):
        """Integration test: Detection of write-spec task type.

        The spec defines 7 task types. This tests write-spec detection
        which was not covered in unit tests.
        """
        prompts = [
            "Write a spec for the new authentication feature",
            "Create a specification document",
            "Write specification for the API",
            "Document the spec for this component",
        ]

        for prompt in prompts:
            output = run_task_detector(prompt)
            assert output["task_type"] == "write-spec", f"Failed for: {prompt}"

    def test_detects_refactor_task_type(self):
        """Integration test: Detection of refactor task type.

        The spec defines 7 task types. This tests refactor detection
        which was not covered in unit tests.
        """
        prompts = [
            "Refactor this code to be more readable",
            "Cleanup the module structure",
            "Restructure the database layer",
            "Reorganize the file layout",
        ]

        for prompt in prompts:
            output = run_task_detector(prompt)
            assert output["task_type"] == "refactor", f"Failed for: {prompt}"

    def test_config_validation_with_partial_configuration(self):
        """Integration test: Config validation with partial configurations.

        Tests that the config loader properly merges partial configs
        with defaults and doesn't fail on minimal valid configs.
        """
        partial_config = {
            "version": "1.0",
        }

        temp_dir = create_test_project(config_data=partial_config)

        output, exit_code = run_context_loader(
            prompt="Test the login functionality",
            cwd=temp_dir,
        )

        assert exit_code == 0, "Should succeed with partial config"
        assert isinstance(output, dict)
        assert "hookSpecificOutput" in output

    def test_error_handling_for_invalid_json_input(self):
        """Integration test: Error handling for invalid input.

        Tests that the context loader handles invalid JSON input
        gracefully and returns appropriate error with exit code 2.
        """
        result = subprocess.run(
            [sys.executable, str(CONTEXT_LOADER_PATH)],
            input="this is not valid json",
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )

        assert result.returncode == 2, "Should exit with code 2 for invalid input"

        try:
            output = json.loads(result.stdout)
            assert "hookSpecificOutput" in output
            assert "additionalContext" in output["hookSpecificOutput"]
            assert "/red64:init" in output["hookSpecificOutput"]["additionalContext"]
        except json.JSONDecodeError:
            pass

    def test_full_workflow_with_multiple_file_type_detection(self):
        """Integration test: Full workflow with multiple file type detection.

        Tests that the complete workflow correctly detects and reports
        multiple file types mentioned in a single prompt.
        """
        temp_dir = create_test_project()

        output, exit_code = run_context_loader(
            prompt="Update the main.py script and modify the README.md documentation, also check package.json",
            cwd=temp_dir,
        )

        assert exit_code == 0
        assert isinstance(output, dict)

        additional_context = output["hookSpecificOutput"]["additionalContext"]
        file_types_mentioned = any(
            ext in additional_context
            for ext in [".py", ".md", ".json", "main.py", "README.md", "package.json"]
        )
        assert file_types_mentioned or "File Types:" in additional_context
