"""Tests for standards plugin template validation.

Tests cover:
- plugin.json has required 'category: "standards"' field
- standards.json file pattern parsing (glob matching)
- Plugin directory structure validation (skills/, hooks/ directories exist)
"""

import fnmatch
import json
import sys
from pathlib import Path

import pytest


PLUGINS_DIR = Path(__file__).parent.parent.parent
STANDARDS_TEMPLATE_DIR = PLUGINS_DIR / "standards-template"


class TestPluginJsonStandardsCategory:
    """Tests for plugin.json category field validation."""

    def test_plugin_json_has_category_field(self):
        """Test: plugin.json includes 'category' field."""
        plugin_json_path = STANDARDS_TEMPLATE_DIR / ".claude-plugin" / "plugin.json"

        assert plugin_json_path.exists(), f"plugin.json not found at {plugin_json_path}"

        with open(plugin_json_path) as f:
            plugin_config = json.load(f)

        assert "category" in plugin_config, "plugin.json must include 'category' field"

    def test_plugin_json_category_is_standards(self):
        """Test: plugin.json category field is set to 'standards'."""
        plugin_json_path = STANDARDS_TEMPLATE_DIR / ".claude-plugin" / "plugin.json"

        with open(plugin_json_path) as f:
            plugin_config = json.load(f)

        assert plugin_config["category"] == "standards", (
            f"Expected category 'standards', got '{plugin_config.get('category')}'"
        )


class TestStandardsJsonPatternParsing:
    """Tests for standards.json file pattern parsing."""

    def test_standards_json_has_file_patterns_field(self):
        """Test: standards.json includes 'file_patterns' array."""
        standards_json_path = STANDARDS_TEMPLATE_DIR / "standards.json"

        assert standards_json_path.exists(), f"standards.json not found at {standards_json_path}"

        with open(standards_json_path) as f:
            standards_config = json.load(f)

        assert "file_patterns" in standards_config, "standards.json must include 'file_patterns' field"
        assert isinstance(standards_config["file_patterns"], list), "'file_patterns' must be an array"

    def test_file_patterns_glob_matching_works(self):
        """Test: file patterns can be used for glob matching."""
        standards_json_path = STANDARDS_TEMPLATE_DIR / "standards.json"

        with open(standards_json_path) as f:
            standards_config = json.load(f)

        patterns = standards_config["file_patterns"]
        assert len(patterns) > 0, "file_patterns must have at least one pattern"

        test_file = "example.ts"
        matches = any(fnmatch.fnmatch(test_file, pattern) for pattern in patterns)
        assert matches, f"Expected patterns {patterns} to match '{test_file}'"


class TestPluginDirectoryStructure:
    """Tests for plugin directory structure validation."""

    def test_skills_directory_exists(self):
        """Test: skills/ directory exists in plugin template."""
        skills_dir = STANDARDS_TEMPLATE_DIR / "skills"

        assert skills_dir.exists(), f"skills/ directory not found at {skills_dir}"
        assert skills_dir.is_dir(), f"{skills_dir} must be a directory"

    def test_hooks_directory_exists(self):
        """Test: hooks/ directory exists in plugin template."""
        hooks_dir = STANDARDS_TEMPLATE_DIR / "hooks"

        assert hooks_dir.exists(), f"hooks/ directory not found at {hooks_dir}"
        assert hooks_dir.is_dir(), f"{hooks_dir} must be a directory"

    def test_hooks_json_is_empty(self):
        """Test: hooks/hooks.json contains empty hooks object."""
        hooks_json_path = STANDARDS_TEMPLATE_DIR / "hooks" / "hooks.json"

        assert hooks_json_path.exists(), f"hooks.json not found at {hooks_json_path}"

        with open(hooks_json_path) as f:
            hooks_config = json.load(f)

        assert hooks_config == {"hooks": {}}, (
            f"Expected empty hooks object {{'hooks': {{}}}}, got {hooks_config}"
        )
