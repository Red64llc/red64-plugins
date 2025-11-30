"""Tests for planning command behavior.

Tests cover:
- /red64:plan-mission creates file at correct path when missing
- /red64:plan-mission skips with message when file exists
- Success message includes created file path
- Skip message follows pattern from red64-init.md
"""

import shutil
import tempfile
from pathlib import Path

import pytest


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def read_template(name: str) -> str:
    """Read a template file and return its content."""
    template_path = TEMPLATES_DIR / name
    return template_path.read_text()


def simulate_plan_command(
    project_root: Path,
    file_name: str,
    template_name: str,
) -> tuple[bool, str]:
    """Simulate a planning command behavior.

    Args:
        project_root: Root directory of the project.
        file_name: Target file name (e.g., "mission.md").
        template_name: Template file name (e.g., "mission-template.md").

    Returns:
        Tuple of (created: bool, message: str)
        - created: True if new file was created, False if skipped
        - message: Success or skip message
    """
    red64_dir = project_root / ".red64"
    product_dir = red64_dir / "product"
    target_path = product_dir / file_name

    if target_path.exists():
        return False, f"Skipped: .red64/product/{file_name} already exists. No changes made."

    product_dir.mkdir(parents=True, exist_ok=True)

    template_content = read_template(template_name)
    target_path.write_text(template_content)

    return True, f"Success: Created .red64/product/{file_name}"


class TestPlanMissionCommand:
    """Test suite for /red64:plan-mission command behavior."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_creates_file_at_correct_path_when_missing(self, temp_project: Path):
        """Test: /red64:plan-mission creates file at correct path when missing."""
        target_path = temp_project / ".red64" / "product" / "mission.md"
        assert not target_path.exists()

        created, message = simulate_plan_command(
            temp_project,
            "mission.md",
            "mission-template.md",
        )

        assert created is True
        assert target_path.exists()
        assert target_path.is_file()

    def test_skips_with_message_when_file_exists(self, temp_project: Path):
        """Test: /red64:plan-mission skips with message when file exists."""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True, exist_ok=True)
        target_path = product_dir / "mission.md"
        target_path.write_text("# Existing Mission\n\nCustom content.")

        created, message = simulate_plan_command(
            temp_project,
            "mission.md",
            "mission-template.md",
        )

        assert created is False
        assert "Skipped" in message
        assert "already exists" in message

        content = target_path.read_text()
        assert "Custom content" in content

    def test_success_message_includes_file_path(self, temp_project: Path):
        """Test: Success message includes created file path."""
        created, message = simulate_plan_command(
            temp_project,
            "mission.md",
            "mission-template.md",
        )

        assert created is True
        assert "Success" in message
        assert ".red64/product/mission.md" in message

    def test_skip_message_follows_pattern(self, temp_project: Path):
        """Test: Skip message follows pattern from red64-init.md.

        The skip message should follow the format:
        "Skipped: [path] already exists. No changes made."
        """
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True, exist_ok=True)
        target_path = product_dir / "mission.md"
        target_path.write_text("# Existing Mission")

        created, message = simulate_plan_command(
            temp_project,
            "mission.md",
            "mission-template.md",
        )

        assert created is False
        assert message == "Skipped: .red64/product/mission.md already exists. No changes made."
