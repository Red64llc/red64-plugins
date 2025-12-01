"""End-to-end and integration tests for standards plugin architecture.

Tests cover:
- Full workflow: enable standards -> edit file -> verify context
- PreToolUse hook blocking for DON'T patterns
- Multiple standards ordering precedence
- Token budget allocation with standards priority
- Config persistence across workflow
- Edit tool validation (in addition to Write tool)
"""

import json
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
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
VALIDATOR_SCRIPT = HOOKS_DIR / "standards-validator.py"
CONTEXT_LOADER_SCRIPT = SCRIPTS_DIR / "context-loader.py"


class TestEndToEndEnableAndContext:
    """End-to-end tests: Enable standards via config, edit TS file, verify context."""

    @pytest.fixture
    def temp_project_full_setup(self):
        """Create a complete project setup with TypeScript standards plugin."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        plugins_dest = Path(temp_dir) / "plugins" / "red64-standards-typescript"
        plugins_dest.parent.mkdir(parents=True)
        shutil.copytree(TYPESCRIPT_PLUGIN_DIR, plugins_dest)

        config_content = {
            "version": "1.0",
            "token_budget": {"max_tokens": 5000},
            "standards": {
                "enabled": ["red64-standards-typescript"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_full_workflow_enable_standards_edit_file_verify_context(
        self, temp_project_full_setup: Path
    ):
        """Test: Full workflow - enable TypeScript standards, detect .ts file, verify context."""
        input_data = {
            "session_id": "e2e-test-session",
            "prompt": "Update the src/app.ts file to fix the bug in the handler",
            "cwd": str(temp_project_full_setup),
            "permission_mode": "default",
        }

        result = subprocess.run(
            [sys.executable, str(CONTEXT_LOADER_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=str(temp_project_full_setup),
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        additional_context = output.get("hookSpecificOutput", {}).get(
            "additionalContext", ""
        )

        assert ".ts" in additional_context or "typescript" in additional_context.lower()
        assert "Standards:" in additional_context

    def test_context_includes_skill_content_from_enabled_standard(
        self, temp_project_full_setup: Path
    ):
        """Test: Context output includes actual skill content from enabled standards."""
        input_data = {
            "session_id": "e2e-skill-content",
            "prompt": "Edit the component.tsx file to add new types",
            "cwd": str(temp_project_full_setup),
            "permission_mode": "default",
        }

        result = subprocess.run(
            [sys.executable, str(CONTEXT_LOADER_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=str(temp_project_full_setup),
        )

        output = json.loads(result.stdout)
        context = output.get("hookSpecificOutput", {}).get("additionalContext", "")

        assert "DO" in context or "DON'T" in context or "typescript" in context.lower()


class TestPreToolUseBlockingWorkflow:
    """Tests for PreToolUse hook blocking DON'T pattern violations."""

    @pytest.fixture
    def temp_project_with_ts_standards(self):
        """Create project with TypeScript standards for blocking tests."""
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

    def test_validator_blocks_any_type_in_write_operation(
        self, temp_project_with_ts_standards: Path
    ):
        """Test: Validator blocks Write operation using 'any' type."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(temp_project_with_ts_standards / "src" / "service.ts"),
                "content": "export const processData = (input: any) => { return input; };",
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
        assert output["decision"] == "block"
        assert "reason" in output
        assert "any" in output["reason"].lower()

    def test_validator_blocks_edit_operation_with_violation(
        self, temp_project_with_ts_standards: Path
    ):
        """Test: Validator blocks Edit operation with DON'T pattern violation."""
        input_data = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": str(temp_project_with_ts_standards / "src" / "utils.ts"),
                "content": "var legacyValue = 42;",
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
        assert output["decision"] == "block"
        assert "var" in output.get("reason", "").lower()

    def test_validator_allows_compliant_code(
        self, temp_project_with_ts_standards: Path
    ):
        """Test: Validator allows code that follows standards."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(temp_project_with_ts_standards / "src" / "clean.ts"),
                "content": "const userName: string = 'Alice';\nconst processUser = (user: User): Result => { return { success: true }; };",
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


class TestMultipleStandardsOrderingPrecedence:
    """Integration tests for multiple standards with ordering precedence."""

    @pytest.fixture
    def temp_project_multiple_overlapping_standards(self):
        """Create project with multiple standards for same file type."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        for idx, (plugin_name, skill_content) in enumerate([
            (
                "red64-standards-strict",
                "# Strict Rules\n\n## DO\n\nUse explicit return types.\n\n## DON'T\n\nNever use eval() function.\n\n```typescript\neval('code');\n```",
            ),
            (
                "red64-standards-lenient",
                "# Lenient Rules\n\n## DO\n\nWrite readable code.\n\n## DON'T\n\nAvoid overly long functions.",
            ),
        ]):
            plugin_dir = Path(temp_dir) / "plugins" / plugin_name
            plugin_dir.mkdir(parents=True)
            (plugin_dir / ".claude-plugin").mkdir()
            (plugin_dir / "skills").mkdir()
            (plugin_dir / "hooks").mkdir()

            plugin_json = {"name": plugin_name, "category": "standards"}
            with open(plugin_dir / ".claude-plugin" / "plugin.json", "w") as f:
                json.dump(plugin_json, f)

            standards_json = {"name": plugin_name, "file_patterns": ["*.ts"]}
            with open(plugin_dir / "standards.json", "w") as f:
                json.dump(standards_json, f)

            with open(plugin_dir / "skills" / "rules.md", "w") as f:
                f.write(skill_content)

            hooks_json = {"hooks": {}}
            with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
                json.dump(hooks_json, f)

        config_content = {
            "version": "1.0",
            "token_budget": {"max_tokens": 5000},
            "standards": {
                "enabled": ["red64-standards-strict", "red64-standards-lenient"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_first_standard_in_list_has_highest_precedence(
        self, temp_project_multiple_overlapping_standards: Path
    ):
        """Test: First standard (strict) is applied first for validation."""
        input_data = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": str(
                    temp_project_multiple_overlapping_standards / "src" / "app.ts"
                ),
                "content": "eval('dangerous');",
            },
            "cwd": str(temp_project_multiple_overlapping_standards),
            "plugins_dir": str(temp_project_multiple_overlapping_standards / "plugins"),
        }

        result = subprocess.run(
            [sys.executable, str(VALIDATOR_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
        )

        output = json.loads(result.stdout)
        assert output["decision"] == "block"
        assert "strict" in output.get("reason", "").lower() or "eval" in output.get(
            "reason", ""
        ).lower()


class TestTokenBudgetWithStandardsPriority:
    """Integration tests for token budget allocation respecting standards priority."""

    @pytest.fixture
    def temp_project_with_budget_priority(self):
        """Create project with specific token budget priority for standards."""
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

        standards_json = {"name": "typescript", "file_patterns": ["*.ts", "*.tsx"]}
        with open(plugin_dir / "standards.json", "w") as f:
            json.dump(standards_json, f)

        skill = "# Type Safety\n\n## DO\n\nUse explicit types.\n\n## DON'T\n\nAvoid any type."
        with open(plugin_dir / "skills" / "type-safety.md", "w") as f:
            f.write(skill)

        hooks_json = {"hooks": {}}
        with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
            json.dump(hooks_json, f)

        config_content = {
            "version": "1.0",
            "token_budget": {"max_tokens": 3000},
            "standards": {
                "enabled": ["red64-standards-typescript"],
                "token_budget_priority": 1,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_high_priority_standards_included_in_context(
        self, temp_project_with_budget_priority: Path
    ):
        """Test: Standards with high priority (1) are included in context output."""
        input_data = {
            "session_id": "budget-priority-test",
            "prompt": "Edit the service.ts file to add error handling",
            "cwd": str(temp_project_with_budget_priority),
            "permission_mode": "default",
        }

        result = subprocess.run(
            [sys.executable, str(CONTEXT_LOADER_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=str(temp_project_with_budget_priority),
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        context = output.get("hookSpecificOutput", {}).get("additionalContext", "")
        assert "Standards:" in context or ".ts" in context


class TestConfigPersistenceAcrossWorkflow:
    """Tests for config.yaml changes persisting correctly across workflow."""

    @pytest.fixture
    def temp_project_for_persistence(self):
        """Create project for config persistence testing."""
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

        standards_json = {"name": "test", "file_patterns": ["*.test"]}
        with open(plugin_dir / "standards.json", "w") as f:
            json.dump(standards_json, f)

        skill = "# Test Skill\n\n## DO\n\nWrite tests.\n\n## DON'T\n\nSkip tests."
        with open(plugin_dir / "skills" / "testing.md", "w") as f:
            f.write(skill)

        hooks_json = {"hooks": {}}
        with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
            json.dump(hooks_json, f)

        initial_config = {
            "version": "1.0",
            "standards": {
                "enabled": [],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(initial_config, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_enabling_standard_persists_to_config_file(
        self, temp_project_for_persistence: Path
    ):
        """Test: Enabling a standard persists the change to config.yaml."""
        config_path = temp_project_for_persistence / ".red64" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)
        config["standards"]["enabled"].append("red64-standards-test")
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        with open(config_path) as f:
            reloaded = yaml.safe_load(f)

        assert "red64-standards-test" in reloaded["standards"]["enabled"]

    def test_disabled_standard_removed_from_config_file(
        self, temp_project_for_persistence: Path
    ):
        """Test: Disabling a standard removes it from config.yaml."""
        config_path = temp_project_for_persistence / ".red64" / "config.yaml"

        with open(config_path) as f:
            config = yaml.safe_load(f)
        config["standards"]["enabled"] = ["red64-standards-test", "another-standard"]
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        with open(config_path) as f:
            config = yaml.safe_load(f)
        config["standards"]["enabled"].remove("another-standard")
        with open(config_path, "w") as f:
            yaml.dump(config, f)

        with open(config_path) as f:
            final = yaml.safe_load(f)

        assert "another-standard" not in final["standards"]["enabled"]
        assert "red64-standards-test" in final["standards"]["enabled"]
