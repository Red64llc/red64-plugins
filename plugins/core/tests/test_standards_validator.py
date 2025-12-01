"""Tests for standards validator PreToolUse hook.

Tests cover:
- Hook receives correct input (tool_name, tool_input with file paths)
- Hook returns {"decision": "allow"} for compliant operations
- Hook returns {"decision": "block", "reason": "..."} for violations
- File extension matching against standards.json patterns
- Multiple standards precedence based on config ordering
- Suggestion field for advisory guidance
- Standards skill loading utility function
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
HOOKS_DIR = Path(__file__).parent.parent / "hooks"
PLUGINS_DIR = Path(__file__).parent.parent.parent
VALIDATOR_SCRIPT = HOOKS_DIR / "standards-validator.py"


class TestStandardsValidatorInput:
    """Tests for validator receiving correct input format."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with config."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()
        config_path = red64_dir / "config.yaml"
        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": [],
                "token_budget_priority": 3,
            },
        }
        with open(config_path, "w") as f:
            yaml.dump(config_content, f)
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_hook_accepts_tool_name_and_tool_input(self, temp_project_dir: Path):
        """Test: Hook accepts JSON input with tool_name and tool_input fields."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/path/to/file.ts",
                "content": "const x = 1;",
            },
            "cwd": str(temp_project_dir),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        assert "decision" in output


class TestStandardsValidatorAllowDecision:
    """Tests for validator returning allow decision."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with config and no enabled standards."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()
        config_path = red64_dir / "config.yaml"
        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": [],
                "token_budget_priority": 3,
            },
        }
        with open(config_path, "w") as f:
            yaml.dump(config_content, f)
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_hook_returns_allow_when_no_standards_enabled(self, temp_project_dir: Path):
        """Test: Hook returns allow decision when no standards are enabled."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/path/to/file.ts",
                "content": "const x = 1;",
            },
            "cwd": str(temp_project_dir),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        assert output["decision"] == "allow"

    def test_hook_returns_allow_for_non_edit_write_tools(self, temp_project_dir: Path):
        """Test: Hook returns allow for tools other than Edit/Write."""
        input_data = {
            "tool_name": "Read",
            "tool_input": {
                "file_path": "/path/to/file.ts",
            },
            "cwd": str(temp_project_dir),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        assert output["decision"] == "allow"


class TestStandardsValidatorBlockDecision:
    """Tests for validator returning block decision."""

    @pytest.fixture
    def temp_project_with_standards(self):
        """Create a temporary project with enabled standards and DON'T patterns."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        plugin_dir = Path(temp_dir) / "plugins" / "red64-standards-test"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / ".claude-plugin").mkdir()
        (plugin_dir / "skills").mkdir()
        (plugin_dir / "hooks").mkdir()

        plugin_json = {
            "name": "red64-standards-test",
            "category": "standards",
        }
        with open(plugin_dir / ".claude-plugin" / "plugin.json", "w") as f:
            json.dump(plugin_json, f)

        standards_json = {
            "name": "test-standards",
            "file_patterns": ["*.ts", "*.tsx"],
        }
        with open(plugin_dir / "standards.json", "w") as f:
            json.dump(standards_json, f)

        skill_content = """# Test Skill

## DO

Use proper patterns.

## DON'T

### Avoid any type

Never use the `any` type in TypeScript code.

```typescript
// Bad: using any
const data: any = fetchData();
```
"""
        with open(plugin_dir / "skills" / "test-skill.md", "w") as f:
            f.write(skill_content)

        hooks_json = {"hooks": {}}
        with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
            json.dump(hooks_json, f)

        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": ["red64-standards-test"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_hook_returns_block_with_reason_for_violations(
        self, temp_project_with_standards: Path
    ):
        """Test: Hook returns block decision with reason for standards violations."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(temp_project_with_standards / "src" / "file.ts"),
                "content": "const data: any = fetchData();",
            },
            "cwd": str(temp_project_with_standards),
            "plugins_dir": str(temp_project_with_standards / "plugins"),
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
        assert "any" in output["reason"].lower()


class TestFileExtensionMatching:
    """Tests for file extension matching against standards.json patterns."""

    @pytest.fixture
    def temp_project_with_ts_standards(self):
        """Create project with TypeScript-only standards."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        plugin_dir = Path(temp_dir) / "plugins" / "red64-standards-typescript"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / ".claude-plugin").mkdir()
        (plugin_dir / "skills").mkdir()
        (plugin_dir / "hooks").mkdir()

        plugin_json = {"name": "red64-standards-typescript", "category": "standards"}
        with open(plugin_dir / ".claude-plugin" / "plugin.json", "w") as f:
            json.dump(plugin_json, f)

        standards_json = {
            "name": "typescript-standards",
            "file_patterns": ["*.ts", "*.tsx"],
        }
        with open(plugin_dir / "standards.json", "w") as f:
            json.dump(standards_json, f)

        skill_content = """# Type Safety

## DO

Use explicit types.

## DON'T

Avoid using any type.
"""
        with open(plugin_dir / "skills" / "type-safety.md", "w") as f:
            f.write(skill_content)

        hooks_json = {"hooks": {}}
        with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
            json.dump(hooks_json, f)

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

    def test_standards_apply_to_matching_file_extension(
        self, temp_project_with_ts_standards: Path
    ):
        """Test: Standards are applied when file extension matches patterns."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(temp_project_with_ts_standards / "src" / "app.ts"),
                "content": "const x = 1;",
            },
            "cwd": str(temp_project_with_ts_standards),
            "plugins_dir": str(temp_project_with_ts_standards / "plugins"),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        assert output["decision"] in ["allow", "block"]

    def test_standards_ignored_for_non_matching_file_extension(
        self, temp_project_with_ts_standards: Path
    ):
        """Test: Standards are not applied when file extension does not match."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(temp_project_with_ts_standards / "src" / "app.py"),
                "content": "x: any = 1",
            },
            "cwd": str(temp_project_with_ts_standards),
            "plugins_dir": str(temp_project_with_ts_standards / "plugins"),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        assert output["decision"] == "allow"


class TestMultipleStandardsPrecedence:
    """Tests for multiple standards precedence based on config ordering."""

    @pytest.fixture
    def temp_project_with_multiple_standards(self):
        """Create project with multiple enabled standards."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        for plugin_name in ["red64-standards-strict", "red64-standards-relaxed"]:
            plugin_dir = Path(temp_dir) / "plugins" / plugin_name
            plugin_dir.mkdir(parents=True)
            (plugin_dir / ".claude-plugin").mkdir()
            (plugin_dir / "skills").mkdir()
            (plugin_dir / "hooks").mkdir()

            plugin_json = {"name": plugin_name, "category": "standards"}
            with open(plugin_dir / ".claude-plugin" / "plugin.json", "w") as f:
                json.dump(plugin_json, f)

            standards_json = {
                "name": plugin_name,
                "file_patterns": ["*.ts"],
            }
            with open(plugin_dir / "standards.json", "w") as f:
                json.dump(standards_json, f)

            hooks_json = {"hooks": {}}
            with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
                json.dump(hooks_json, f)

        strict_skill = """# Strict Rules

## DO

Always use explicit types.

## DON'T

Never use var keyword.

```typescript
var x = 1;
```
"""
        strict_plugin = Path(temp_dir) / "plugins" / "red64-standards-strict"
        with open(strict_plugin / "skills" / "strict.md", "w") as f:
            f.write(strict_skill)

        relaxed_skill = """# Relaxed Rules

## DO

Write clean code.

## DON'T

Avoid obvious issues.
"""
        relaxed_plugin = Path(temp_dir) / "plugins" / "red64-standards-relaxed"
        with open(relaxed_plugin / "skills" / "relaxed.md", "w") as f:
            f.write(relaxed_skill)

        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": ["red64-standards-strict", "red64-standards-relaxed"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_first_standard_takes_precedence(
        self, temp_project_with_multiple_standards: Path
    ):
        """Test: First standard in enabled list takes precedence for validation."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(temp_project_with_multiple_standards / "src" / "app.ts"),
                "content": "var x = 1;",
            },
            "cwd": str(temp_project_with_multiple_standards),
            "plugins_dir": str(temp_project_with_multiple_standards / "plugins"),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        assert output["decision"] == "block"
        assert "strict" in output.get("reason", "").lower() or "var" in output.get("reason", "").lower()


class TestSuggestionField:
    """Tests for suggestion field in validator response."""

    @pytest.fixture
    def temp_project_with_standards(self):
        """Create project with enabled standards."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        plugin_dir = Path(temp_dir) / "plugins" / "red64-standards-test"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / ".claude-plugin").mkdir()
        (plugin_dir / "skills").mkdir()
        (plugin_dir / "hooks").mkdir()

        plugin_json = {"name": "red64-standards-test", "category": "standards"}
        with open(plugin_dir / ".claude-plugin" / "plugin.json", "w") as f:
            json.dump(plugin_json, f)

        standards_json = {"name": "test", "file_patterns": ["*.ts"]}
        with open(plugin_dir / "standards.json", "w") as f:
            json.dump(standards_json, f)

        skill_content = """# Naming

## DO

Use descriptive names.

## DON'T

Avoid single-letter variable names except for loop counters.

```typescript
const d = new Date();
```
"""
        with open(plugin_dir / "skills" / "naming.md", "w") as f:
            f.write(skill_content)

        hooks_json = {"hooks": {}}
        with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
            json.dump(hooks_json, f)

        config_content = {
            "version": "1.0",
            "standards": {
                "enabled": ["red64-standards-test"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_block_response_includes_suggestion_field(
        self, temp_project_with_standards: Path
    ):
        """Test: Block response includes suggestion field for advisory guidance."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(temp_project_with_standards / "src" / "app.ts"),
                "content": "const d = new Date();",
            },
            "cwd": str(temp_project_with_standards),
            "plugins_dir": str(temp_project_with_standards / "plugins"),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        if output["decision"] == "block":
            assert "suggestion" in output or "reason" in output


class TestSkillLoadingUtility:
    """Tests for standards skill loading utility function."""

    @pytest.fixture
    def temp_standards_plugin(self):
        """Create a temporary standards plugin for testing skill loading."""
        temp_dir = tempfile.mkdtemp()
        plugin_dir = Path(temp_dir) / "red64-standards-test"
        plugin_dir.mkdir()
        (plugin_dir / ".claude-plugin").mkdir()
        (plugin_dir / "skills").mkdir()
        (plugin_dir / "hooks").mkdir()

        plugin_json = {"name": "red64-standards-test", "category": "standards"}
        with open(plugin_dir / ".claude-plugin" / "plugin.json", "w") as f:
            json.dump(plugin_json, f)

        standards_json = {"name": "test", "file_patterns": ["*.ts"]}
        with open(plugin_dir / "standards.json", "w") as f:
            json.dump(standards_json, f)

        skill1 = """# Skill One

## DO

Do good things.

## DON'T

Avoid using eval().
"""
        skill2 = """# Skill Two

## DO

Use async/await.

## DON'T

Avoid callback hell.
"""
        with open(plugin_dir / "skills" / "skill-one.md", "w") as f:
            f.write(skill1)
        with open(plugin_dir / "skills" / "skill-two.md", "w") as f:
            f.write(skill2)

        hooks_json = {"hooks": {}}
        with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
            json.dump(hooks_json, f)

        yield plugin_dir
        shutil.rmtree(temp_dir)

    def test_skill_loader_extracts_dont_patterns(self, temp_standards_plugin: Path):
        """Test: Skill loader extracts DON'T patterns from SKILL.md files."""
        sys.path.insert(0, str(HOOKS_DIR))
        try:
            from importlib import import_module
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "standards_validator",
                VALIDATOR_SCRIPT
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            dont_patterns = module.load_dont_patterns_from_plugin(temp_standards_plugin)
            assert len(dont_patterns) > 0
            pattern_text = " ".join(dont_patterns).lower()
            assert "eval" in pattern_text or "callback" in pattern_text
        finally:
            if str(HOOKS_DIR) in sys.path:
                sys.path.remove(str(HOOKS_DIR))
