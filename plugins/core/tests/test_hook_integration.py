"""Tests for hook integration with product context.

Tests cover:
- Product-context.py is called on UserPromptSubmit via context-loader.py
- Product context appears in additionalContext output
- Integration respects token budget from config.yaml
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
    mission_content: str | None = None,
    roadmap_content: str | None = None,
) -> str:
    """Create a temporary project directory with optional product files.

    Args:
        with_config: Whether to create config.yaml.
        config_data: Custom config data (uses defaults if None).
        mission_content: Content for mission.md (None means no file).
        roadmap_content: Content for roadmap.md (None means no file).

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

    if mission_content is not None or roadmap_content is not None:
        product_dir = Path(temp_dir) / ".red64" / "product"
        product_dir.mkdir(parents=True, exist_ok=True)

        if mission_content is not None:
            mission_path = product_dir / "mission.md"
            with open(mission_path, "w") as f:
                f.write(mission_content)

        if roadmap_content is not None:
            roadmap_path = product_dir / "roadmap.md"
            with open(roadmap_path, "w") as f:
                f.write(roadmap_content)

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


class TestHookIntegration:
    """Test suite for product context hook integration."""

    def test_product_context_called_on_user_prompt_submit(self):
        """Test: Product-context.py is called on UserPromptSubmit.

        When a prompt is submitted and product files exist, the context-loader
        should invoke product-context.py and include its output.
        """
        mission_content = """# Product Mission

## Pitch

**IntegrationTestApp** is a testing application. It verifies hook integrations work correctly.

## The Problem

Testing is difficult. Integration tests help catch issues early.

## Key Features

- **Feature One:** Validates hook behavior
- **Feature Two:** Tests context injection
"""
        roadmap_content = """# Product Roadmap

## Milestone 1: Testing

1. [ ] Implement hook integration tests -- Verify context injection `S`
"""
        temp_dir = create_temp_project(
            with_config=True,
            mission_content=mission_content,
            roadmap_content=roadmap_content,
        )

        output, exit_code = run_context_loader(
            prompt="Implement a new feature",
            cwd=temp_dir,
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        assert "hookSpecificOutput" in output
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "Product Context" in additional_context

    def test_product_context_appears_in_additional_context(self):
        """Test: Product context appears in additionalContext output.

        The hook output should include Product Context section with
        Product Mission and Current Work Item subheaders when product
        files are present.
        """
        mission_content = """# Product Mission

## Pitch

**ContextTestApp** provides context testing. It helps verify output format.

## The Problem

Output format validation is important. This tests the format.

## Key Features

- **Validation:** Validates output structure
"""
        roadmap_content = """# Product Roadmap

## Milestone 1: Context Testing

1. [x] Completed item -- Already done `S`
2. [ ] Current work item -- This should appear in context `M`
3. [ ] Future item -- Not yet started `L`
"""
        temp_dir = create_temp_project(
            with_config=True,
            mission_content=mission_content,
            roadmap_content=roadmap_content,
        )

        output, exit_code = run_context_loader(
            prompt="Check the current work",
            cwd=temp_dir,
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        additional_context = output["hookSpecificOutput"]["additionalContext"]

        assert "## Product Context" in additional_context
        assert "### Product Mission" in additional_context
        assert "### Current Work Item" in additional_context
        assert "Current work item" in additional_context
        assert "Context Testing" in additional_context

    def test_integration_respects_token_budget(self):
        """Test: Integration respects token budget from config.yaml.

        The context loader should respect the token budget configuration
        even when product context is included. With a very small budget,
        the output should still be bounded.
        """
        config_data = {
            "version": "1.0",
            "token_budget": {
                "max_tokens": 500,
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

        mission_content = """# Product Mission

## Pitch

**BudgetTestApp** tests token budgets. It verifies the budget is respected.

## The Problem

Token limits exist. We must respect them.

## Key Features

- **Budget Enforcement:** Respects token limits
"""
        roadmap_content = """# Product Roadmap

## Milestone 1: Budget Testing

1. [ ] Test token budget -- Verify limits are respected `S`
"""
        temp_dir = create_temp_project(
            with_config=True,
            config_data=config_data,
            mission_content=mission_content,
            roadmap_content=roadmap_content,
        )

        output, exit_code = run_context_loader(
            prompt="Check the budget handling",
            cwd=temp_dir,
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        additional_context = output["hookSpecificOutput"]["additionalContext"]

        # Verify output exists and is reasonable in size
        # The token budget affects selection, not truncation of individual items
        assert len(additional_context) > 0
        assert len(additional_context) < 10000  # Reasonable upper bound

    def test_graceful_degradation_without_product_docs(self):
        """Test: Graceful degradation if product docs missing.

        When product documents are not present, the context loader should
        continue to function normally without product context, rather than
        failing entirely.
        """
        temp_dir = create_temp_project(
            with_config=True,
            mission_content=None,
            roadmap_content=None,
        )

        output, exit_code = run_context_loader(
            prompt="Implement a new feature",
            cwd=temp_dir,
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        assert "hookSpecificOutput" in output
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        # Should still have Red64 Context section
        assert "Red64 Context" in additional_context
