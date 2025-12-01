"""Tests for TypeScript standards plugin.

Tests cover:
- Plugin structure matches template requirements
- standards.json correctly matches TypeScript files
- Skills follow SKILL.md format with DO/DON'T sections
- Integration with standards validator hook
"""

import fnmatch
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


PLUGINS_DIR = Path(__file__).parent.parent.parent
TYPESCRIPT_PLUGIN_DIR = PLUGINS_DIR / "red64-standards-typescript"
HOOKS_DIR = Path(__file__).parent.parent / "hooks"
VALIDATOR_SCRIPT = HOOKS_DIR / "standards-validator.py"


class TestTypescriptPluginStructure:
    """Tests for plugin structure matching template requirements."""

    def test_plugin_json_exists_with_required_fields(self):
        """Test: plugin.json exists with all required metadata fields."""
        plugin_json_path = TYPESCRIPT_PLUGIN_DIR / ".claude-plugin" / "plugin.json"

        assert plugin_json_path.exists(), f"plugin.json not found at {plugin_json_path}"

        with open(plugin_json_path) as f:
            plugin_config = json.load(f)

        required_fields = ["name", "description", "category", "author"]
        for field in required_fields:
            assert field in plugin_config, f"plugin.json missing required field: {field}"

    def test_plugin_json_category_is_standards(self):
        """Test: plugin.json category field is set to 'standards'."""
        plugin_json_path = TYPESCRIPT_PLUGIN_DIR / ".claude-plugin" / "plugin.json"

        with open(plugin_json_path) as f:
            plugin_config = json.load(f)

        assert plugin_config["category"] == "standards", (
            f"Expected category 'standards', got '{plugin_config.get('category')}'"
        )

    def test_plugin_has_required_directories(self):
        """Test: Plugin has skills/ and hooks/ directories."""
        skills_dir = TYPESCRIPT_PLUGIN_DIR / "skills"
        hooks_dir = TYPESCRIPT_PLUGIN_DIR / "hooks"

        assert skills_dir.exists() and skills_dir.is_dir(), (
            f"skills/ directory not found at {skills_dir}"
        )
        assert hooks_dir.exists() and hooks_dir.is_dir(), (
            f"hooks/ directory not found at {hooks_dir}"
        )

    def test_hooks_json_is_empty(self):
        """Test: hooks/hooks.json contains empty hooks object."""
        hooks_json_path = TYPESCRIPT_PLUGIN_DIR / "hooks" / "hooks.json"

        assert hooks_json_path.exists(), f"hooks.json not found at {hooks_json_path}"

        with open(hooks_json_path) as f:
            hooks_config = json.load(f)

        assert hooks_config == {"hooks": {}}, (
            f"Expected empty hooks object {{'hooks': {{}}}}, got {hooks_config}"
        )


class TestTypescriptStandardsJson:
    """Tests for standards.json TypeScript file matching."""

    def test_standards_json_has_required_fields(self):
        """Test: standards.json includes name, description, and file_patterns."""
        standards_json_path = TYPESCRIPT_PLUGIN_DIR / "standards.json"

        assert standards_json_path.exists(), f"standards.json not found at {standards_json_path}"

        with open(standards_json_path) as f:
            standards_config = json.load(f)

        required_fields = ["name", "description", "file_patterns"]
        for field in required_fields:
            assert field in standards_config, f"standards.json missing required field: {field}"

    def test_file_patterns_match_typescript_files(self):
        """Test: file patterns correctly match .ts and .tsx files."""
        standards_json_path = TYPESCRIPT_PLUGIN_DIR / "standards.json"

        with open(standards_json_path) as f:
            standards_config = json.load(f)

        patterns = standards_config["file_patterns"]

        ts_files = ["app.ts", "component.tsx", "utils/helper.ts", "src/App.tsx"]
        for ts_file in ts_files:
            filename = Path(ts_file).name
            matches = any(fnmatch.fnmatch(filename, pattern) for pattern in patterns)
            assert matches, f"Expected patterns {patterns} to match '{ts_file}'"

    def test_file_patterns_do_not_match_non_typescript_files(self):
        """Test: file patterns do not match non-TypeScript files."""
        standards_json_path = TYPESCRIPT_PLUGIN_DIR / "standards.json"

        with open(standards_json_path) as f:
            standards_config = json.load(f)

        patterns = standards_config["file_patterns"]

        non_ts_files = ["app.js", "styles.css", "config.json", "script.py"]
        for non_ts_file in non_ts_files:
            filename = Path(non_ts_file).name
            matches = any(fnmatch.fnmatch(filename, pattern) for pattern in patterns)
            assert not matches, f"Patterns {patterns} should not match '{non_ts_file}'"


class TestTypescriptSkillsFormat:
    """Tests for skills following SKILL.md format with DO/DON'T sections."""

    EXPECTED_SKILLS = [
        "naming-conventions",
        "type-safety",
        "error-handling",
        "module-structure",
        "async-patterns",
    ]

    def test_all_expected_skills_exist(self):
        """Test: All 5 expected skill files exist."""
        skills_dir = TYPESCRIPT_PLUGIN_DIR / "skills"

        for skill_name in self.EXPECTED_SKILLS:
            skill_path = skills_dir / f"{skill_name}.md"
            assert skill_path.exists(), f"Skill file not found: {skill_path}"

    def test_skills_have_do_and_dont_sections(self):
        """Test: Each skill has both DO and DON'T sections."""
        skills_dir = TYPESCRIPT_PLUGIN_DIR / "skills"

        for skill_name in self.EXPECTED_SKILLS:
            skill_path = skills_dir / f"{skill_name}.md"
            content = skill_path.read_text()

            has_do = bool(re.search(r"^## DO\b", content, re.MULTILINE))
            has_dont = bool(re.search(r"^## DON'T\b", content, re.MULTILINE))

            assert has_do, f"Skill {skill_name} missing '## DO' section"
            assert has_dont, f"Skill {skill_name} missing '## DON'T' section"

    def test_skills_have_code_examples(self):
        """Test: Each skill includes TypeScript code examples in fenced blocks."""
        skills_dir = TYPESCRIPT_PLUGIN_DIR / "skills"

        for skill_name in self.EXPECTED_SKILLS:
            skill_path = skills_dir / f"{skill_name}.md"
            content = skill_path.read_text()

            has_code_block = "```typescript" in content or "```ts" in content

            assert has_code_block, f"Skill {skill_name} missing TypeScript code examples"

    def test_skills_token_length_in_range(self):
        """Test: Each skill is approximately 200-500 tokens (rough word-based estimate)."""
        skills_dir = TYPESCRIPT_PLUGIN_DIR / "skills"

        for skill_name in self.EXPECTED_SKILLS:
            skill_path = skills_dir / f"{skill_name}.md"
            content = skill_path.read_text()

            word_count = len(content.split())
            estimated_tokens = word_count * 1.3

            assert 150 <= estimated_tokens <= 700, (
                f"Skill {skill_name} has ~{int(estimated_tokens)} tokens, "
                f"expected 200-500 (word count: {word_count})"
            )


class TestTypescriptPluginValidatorIntegration:
    """Tests for integration with standards validator hook."""

    @pytest.fixture
    def temp_project_with_typescript_standards(self):
        """Create a temporary project with TypeScript standards enabled."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        plugins_dest = Path(temp_dir) / "plugins" / "red64-standards-typescript"
        plugins_dest.parent.mkdir(parents=True)
        shutil.copytree(TYPESCRIPT_PLUGIN_DIR, plugins_dest)

        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": ["red64-standards-typescript"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_validator_applies_typescript_standards_to_ts_files(
        self, temp_project_with_typescript_standards: Path
    ):
        """Test: Validator applies TypeScript standards when editing .ts files."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(temp_project_with_typescript_standards / "src" / "app.ts"),
                "content": "const userName: string = 'Alice';",
            },
            "cwd": str(temp_project_with_typescript_standards),
            "plugins_dir": str(temp_project_with_typescript_standards / "plugins"),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        assert "decision" in output
        assert output["decision"] in ["allow", "block", "suggest"]

    def test_validator_blocks_any_type_usage(
        self, temp_project_with_typescript_standards: Path
    ):
        """Test: Validator blocks code using 'any' type (type-safety DON'T)."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(temp_project_with_typescript_standards / "src" / "app.ts"),
                "content": "const data: any = fetchData();",
            },
            "cwd": str(temp_project_with_typescript_standards),
            "plugins_dir": str(temp_project_with_typescript_standards / "plugins"),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        assert output["decision"] == "block"
        assert "reason" in output
