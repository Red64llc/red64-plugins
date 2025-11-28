"""Tests for /red64:init command behavior.

Tests cover:
- Directory structure creation
- Default config.yaml generation
- Idempotent behavior (no overwrite)
- Subdirectory creation
"""

import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from config_schema import get_default_config


def simulate_init_command(project_root: Path) -> tuple[bool, str]:
    """Simulate the /red64:init command behavior.

    Returns:
        Tuple of (created: bool, message: str)
        - created: True if new config was created, False if skipped
        - message: Success or skip message
    """
    red64_dir = project_root / ".red64"
    config_path = red64_dir / "config.yaml"

    if config_path.exists():
        return False, "Skipped: .red64/config.yaml already exists. No changes made."

    red64_dir.mkdir(parents=True, exist_ok=True)
    (red64_dir / "product").mkdir(exist_ok=True)
    (red64_dir / "specs").mkdir(exist_ok=True)
    (red64_dir / "metrics").mkdir(exist_ok=True)

    default_config = get_default_config()
    with open(config_path, "w") as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

    return True, "Success: Created .red64/ directory with default configuration."


class TestRed64Init:
    """Test suite for /red64:init command behavior."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_creates_red64_directory_when_missing(self, temp_project: Path):
        """Test: Creates .red64/ directory structure when missing."""
        red64_dir = temp_project / ".red64"
        assert not red64_dir.exists()

        created, message = simulate_init_command(temp_project)

        assert created is True
        assert red64_dir.exists()
        assert red64_dir.is_dir()
        assert "Success" in message

    def test_generates_valid_config_yaml_with_default_schema(self, temp_project: Path):
        """Test: Generates valid config.yaml with default schema."""
        simulate_init_command(temp_project)

        config_path = temp_project / ".red64" / "config.yaml"
        assert config_path.exists()

        with open(config_path) as f:
            config = yaml.safe_load(f)

        expected = get_default_config()
        assert config == expected

        assert config["version"] == "1.0"
        assert config["token_budget"]["max_tokens"] == 3000
        assert config["context_loader"]["enabled"] is True
        assert config["priorities"]["product_mission"] == 1
        assert config["features"]["standards_injection"] is False

    def test_skips_overwrite_when_config_exists(self, temp_project: Path):
        """Test: Skips overwrite when config.yaml already exists (idempotent)."""
        simulate_init_command(temp_project)

        config_path = temp_project / ".red64" / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"version": "custom", "custom_key": "custom_value"}, f)

        created, message = simulate_init_command(temp_project)

        assert created is False
        assert "Skipped" in message
        assert "already exists" in message

        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert config["version"] == "custom"
        assert config["custom_key"] == "custom_value"

    def test_creates_subdirectories(self, temp_project: Path):
        """Test: Creates subdirectories product/, specs/, metrics/."""
        simulate_init_command(temp_project)

        red64_dir = temp_project / ".red64"

        product_dir = red64_dir / "product"
        specs_dir = red64_dir / "specs"
        metrics_dir = red64_dir / "metrics"

        assert product_dir.exists() and product_dir.is_dir()
        assert specs_dir.exists() and specs_dir.is_dir()
        assert metrics_dir.exists() and metrics_dir.is_dir()
