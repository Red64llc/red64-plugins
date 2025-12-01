"""Tests for config schema standards section support.

Tests cover:
- Standards TypedDict structure validation
- merge_with_defaults handles new standards section
- Default values for standards.enabled and standards.token_budget_priority
- Loading config with standards section present vs absent
"""

import sys
import tempfile
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from config_schema import get_default_config, Standards, Red64Config
from config_utils import merge_with_defaults, load_config


class TestStandardsTypedDictStructure:
    """Tests for Standards TypedDict structure validation."""

    def test_standards_typeddict_has_enabled_field(self):
        """Test: Standards TypedDict includes 'enabled' field as list[str]."""
        defaults = get_default_config()

        assert "standards" in defaults
        assert "enabled" in defaults["standards"]
        assert isinstance(defaults["standards"]["enabled"], list)

    def test_standards_typeddict_has_token_budget_priority_field(self):
        """Test: Standards TypedDict includes 'token_budget_priority' field as int."""
        defaults = get_default_config()

        assert "standards" in defaults
        assert "token_budget_priority" in defaults["standards"]
        assert isinstance(defaults["standards"]["token_budget_priority"], int)


class TestMergeWithDefaultsStandards:
    """Tests for merge_with_defaults handling of standards section."""

    def test_merge_applies_standards_defaults_when_section_absent(self):
        """Test: merge_with_defaults applies standards defaults when section is missing."""
        config_data = {
            "version": "1.0",
            "token_budget": {"max_tokens": 3000},
        }

        merged = merge_with_defaults(config_data)

        assert "standards" in merged
        assert merged["standards"]["enabled"] == []
        assert merged["standards"]["token_budget_priority"] == 3

    def test_merge_preserves_custom_standards_values(self):
        """Test: merge_with_defaults preserves custom standards values when provided."""
        config_data = {
            "version": "1.0",
            "standards": {
                "enabled": ["typescript", "python"],
                "token_budget_priority": 2,
            },
        }

        merged = merge_with_defaults(config_data)

        assert merged["standards"]["enabled"] == ["typescript", "python"]
        assert merged["standards"]["token_budget_priority"] == 2

    def test_merge_applies_partial_standards_defaults(self):
        """Test: merge_with_defaults applies defaults for missing fields within standards."""
        config_data = {
            "version": "1.0",
            "standards": {
                "enabled": ["typescript"],
            },
        }

        merged = merge_with_defaults(config_data)

        assert merged["standards"]["enabled"] == ["typescript"]
        assert merged["standards"]["token_budget_priority"] == 3


class TestDefaultStandardsValues:
    """Tests for default values of standards configuration."""

    def test_default_standards_enabled_is_empty_list(self):
        """Test: Default standards.enabled is an empty list."""
        defaults = get_default_config()

        assert defaults["standards"]["enabled"] == []

    def test_default_standards_token_budget_priority_is_3(self):
        """Test: Default standards.token_budget_priority is 3."""
        defaults = get_default_config()

        assert defaults["standards"]["token_budget_priority"] == 3


class TestLoadConfigWithStandards:
    """Tests for loading config with standards section present vs absent."""

    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary directory for config file testing."""
        import shutil

        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_load_config_with_standards_section_present(self, temp_config_dir: Path):
        """Test: load_config correctly loads config with standards section."""
        config_path = temp_config_dir / "config.yaml"
        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": ["typescript"],
                "token_budget_priority": 2,
            },
        }
        with open(config_path, "w") as f:
            yaml.dump(config_content, f)

        loaded = load_config(config_path)

        assert loaded["standards"]["enabled"] == ["typescript"]
        assert loaded["standards"]["token_budget_priority"] == 2

    def test_load_config_with_standards_section_absent(self, temp_config_dir: Path):
        """Test: load_config applies defaults when standards section is absent."""
        config_path = temp_config_dir / "config.yaml"
        config_content = {
            "version": "1.0",
            "token_budget": {"max_tokens": 3000},
        }
        with open(config_path, "w") as f:
            yaml.dump(config_content, f)

        loaded = load_config(config_path)

        assert loaded["standards"]["enabled"] == []
        assert loaded["standards"]["token_budget_priority"] == 3
