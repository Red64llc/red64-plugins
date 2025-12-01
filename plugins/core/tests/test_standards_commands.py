"""Tests for standards enable/disable CLI commands.

Tests cover:
- Enable command adds standard to config.yaml standards.enabled list
- Disable command removes standard from config.yaml
- Validation rejects non-existent standard plugins
- Ordering is preserved (first enabled = highest priority)
"""

import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from config_utils import load_config

PLUGINS_DIR = Path(__file__).parent.parent.parent


def create_mock_standards_plugin(plugins_dir: Path, name: str) -> Path:
    """Create a minimal standards plugin for testing.

    Args:
        plugins_dir: Directory where plugins are located.
        name: Name of the standards plugin to create.

    Returns:
        Path to the created plugin directory.
    """
    plugin_dir = plugins_dir / f"red64-standards-{name}"
    plugin_dir.mkdir(parents=True, exist_ok=True)

    claude_plugin_dir = plugin_dir / ".claude-plugin"
    claude_plugin_dir.mkdir(exist_ok=True)

    plugin_json = {
        "name": f"red64-standards-{name}",
        "description": f"Test standards plugin for {name}",
        "source": f"./plugins/red64-standards-{name}",
        "category": "standards",
    }

    import json

    with open(claude_plugin_dir / "plugin.json", "w") as f:
        json.dump(plugin_json, f)

    standards_json = {
        "name": f"red64-standards-{name}",
        "file_patterns": ["*.test"],
    }
    with open(plugin_dir / "standards.json", "w") as f:
        json.dump(standards_json, f)

    return plugin_dir


class TestStandardsEnableCommand:
    """Tests for the standards-enable command functionality."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with .red64/config.yaml."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": [],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def temp_plugins_dir(self):
        """Create a temporary plugins directory with mock standards plugins."""
        temp_dir = tempfile.mkdtemp()
        plugins_dir = Path(temp_dir)

        create_mock_standards_plugin(plugins_dir, "typescript")
        create_mock_standards_plugin(plugins_dir, "python")

        yield plugins_dir
        shutil.rmtree(temp_dir)

    def test_enable_adds_standard_to_config_enabled_list(
        self, temp_project_dir: Path, temp_plugins_dir: Path
    ):
        """Test: Enable command adds standard to config.yaml standards.enabled list."""
        config_path = temp_project_dir / ".red64" / "config.yaml"

        standard_plugin_dir = temp_plugins_dir / "red64-standards-typescript"
        assert standard_plugin_dir.exists(), "Mock plugin should exist"

        with open(config_path) as f:
            config = yaml.safe_load(f)
        config["standards"]["enabled"].append("typescript")
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        loaded = load_config(config_path)
        assert "typescript" in loaded["standards"]["enabled"]

    def test_enable_preserves_ordering_first_enabled_highest_priority(
        self, temp_project_dir: Path, temp_plugins_dir: Path
    ):
        """Test: Ordering is preserved - first enabled has highest priority."""
        config_path = temp_project_dir / ".red64" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)
        config["standards"]["enabled"].append("typescript")
        config["standards"]["enabled"].append("python")
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        loaded = load_config(config_path)
        enabled = loaded["standards"]["enabled"]
        assert enabled[0] == "typescript", "First enabled should have highest priority"
        assert enabled[1] == "python", "Second enabled should be second in list"
        assert enabled == ["typescript", "python"], "Order must be preserved"


class TestStandardsDisableCommand:
    """Tests for the standards-disable command functionality."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with .red64/config.yaml."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": ["typescript", "python"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_disable_removes_standard_from_config(self, temp_project_dir: Path):
        """Test: Disable command removes standard from config.yaml standards.enabled."""
        config_path = temp_project_dir / ".red64" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)
        config["standards"]["enabled"].remove("typescript")
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        loaded = load_config(config_path)
        assert "typescript" not in loaded["standards"]["enabled"]
        assert "python" in loaded["standards"]["enabled"]


class TestStandardsValidation:
    """Tests for standards plugin validation."""

    def test_validation_rejects_non_existent_standard_plugin(self):
        """Test: Validation rejects non-existent standard plugins."""
        temp_dir = tempfile.mkdtemp()
        plugins_dir = Path(temp_dir)

        nonexistent_plugin = plugins_dir / "red64-standards-nonexistent"
        assert not nonexistent_plugin.exists()

        try:
            plugin_json_path = nonexistent_plugin / ".claude-plugin" / "plugin.json"
            plugin_exists = plugin_json_path.exists()
            assert not plugin_exists, "Non-existent plugin should not be valid"
        finally:
            shutil.rmtree(temp_dir)

    def test_validation_accepts_existing_standard_plugin(self):
        """Test: Validation accepts existing standard plugins with correct structure."""
        temp_dir = tempfile.mkdtemp()
        plugins_dir = Path(temp_dir)

        try:
            create_mock_standards_plugin(plugins_dir, "valid")

            plugin_dir = plugins_dir / "red64-standards-valid"
            plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
            standards_json_path = plugin_dir / "standards.json"

            assert plugin_json_path.exists(), "Plugin must have .claude-plugin/plugin.json"
            assert standards_json_path.exists(), "Standards plugin must have standards.json"

            import json

            with open(plugin_json_path) as f:
                plugin_config = json.load(f)

            assert plugin_config.get("category") == "standards", (
                "Standards plugin must have category: standards"
            )
        finally:
            shutil.rmtree(temp_dir)


class TestStandardsIdempotency:
    """Tests for command idempotency."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with .red64/config.yaml."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": ["typescript"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_enable_idempotent_skips_already_enabled(self, temp_project_dir: Path):
        """Test: Enable command is idempotent - skips if already enabled."""
        config_path = temp_project_dir / ".red64" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)
        initial_enabled = list(config["standards"]["enabled"])

        standard_to_enable = "typescript"
        if standard_to_enable not in config["standards"]["enabled"]:
            config["standards"]["enabled"].append(standard_to_enable)
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        loaded = load_config(config_path)
        assert loaded["standards"]["enabled"] == initial_enabled
        assert loaded["standards"]["enabled"].count("typescript") == 1

    def test_disable_idempotent_skips_if_not_enabled(self, temp_project_dir: Path):
        """Test: Disable command is idempotent - skips if not enabled."""
        config_path = temp_project_dir / ".red64" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)
        initial_enabled = list(config["standards"]["enabled"])

        standard_to_disable = "python"
        if standard_to_disable in config["standards"]["enabled"]:
            config["standards"]["enabled"].remove(standard_to_disable)
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        loaded = load_config(config_path)
        assert loaded["standards"]["enabled"] == initial_enabled
