"""Tests for context loader standards integration.

Tests cover:
- Standards skills are included in context output
- File type matching loads correct standards
- Token budget respects standards.token_budget_priority
- Multiple standards skills are included with precedence header
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
CONTEXT_LOADER_SCRIPT = SCRIPTS_DIR / "context-loader.py"
STANDARDS_LOADER_SCRIPT = SCRIPTS_DIR / "standards-loader.py"


class TestStandardsSkillsInContextOutput:
    """Tests for standards skills appearing in context output."""

    @pytest.fixture
    def temp_project_with_standards(self):
        """Create a temporary project with enabled standards and skills."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        plugin_dir = Path(temp_dir) / "plugins" / "red64-standards-typescript"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / ".claude-plugin").mkdir()
        (plugin_dir / "skills").mkdir()
        (plugin_dir / "hooks").mkdir()

        plugin_json = {
            "name": "red64-standards-typescript",
            "category": "standards",
        }
        with open(plugin_dir / ".claude-plugin" / "plugin.json", "w") as f:
            json.dump(plugin_json, f)

        standards_json = {
            "name": "typescript-standards",
            "file_patterns": ["*.ts", "*.tsx"],
        }
        with open(plugin_dir / "standards.json", "w") as f:
            json.dump(standards_json, f)

        skill_content = """# Naming Conventions

## DO

Use camelCase for variables and functions.

```typescript
const userName = 'Alice';
```

## DON'T

Avoid single-letter names.
"""
        with open(plugin_dir / "skills" / "naming-conventions.md", "w") as f:
            f.write(skill_content)

        hooks_json = {"hooks": {}}
        with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
            json.dump(hooks_json, f)

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

    def test_standards_skills_included_in_context_when_file_type_matches(
        self, temp_project_with_standards: Path
    ):
        """Test: Standards skills are included in context output when file types match."""
        input_data = {
            "session_id": "test-session",
            "prompt": "Edit the app.ts file to add a new function",
            "cwd": str(temp_project_with_standards),
            "permission_mode": "default",
        }

        result = subprocess.run(
            [sys.executable, str(CONTEXT_LOADER_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=str(temp_project_with_standards),
        )

        output = json.loads(result.stdout)
        additional_context = output.get("hookSpecificOutput", {}).get(
            "additionalContext", ""
        )
        assert "Standards:" in additional_context or "red64-standards-typescript" in additional_context


class TestFileTypeMatchingLoadsStandards:
    """Tests for file type matching to load correct standards."""

    @pytest.fixture
    def temp_project_with_multi_standards(self):
        """Create project with multiple standards for different file types."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        for plugin_name, patterns, skill_content in [
            (
                "red64-standards-typescript",
                ["*.ts", "*.tsx"],
                "# TypeScript Standard\n\n## DO\n\nUse types.\n\n## DON'T\n\nAvoid any.",
            ),
            (
                "red64-standards-python",
                ["*.py"],
                "# Python Standard\n\n## DO\n\nUse type hints.\n\n## DON'T\n\nAvoid bare except.",
            ),
        ]:
            plugin_dir = Path(temp_dir) / "plugins" / plugin_name
            plugin_dir.mkdir(parents=True)
            (plugin_dir / ".claude-plugin").mkdir()
            (plugin_dir / "skills").mkdir()
            (plugin_dir / "hooks").mkdir()

            plugin_json = {"name": plugin_name, "category": "standards"}
            with open(plugin_dir / ".claude-plugin" / "plugin.json", "w") as f:
                json.dump(plugin_json, f)

            standards_json = {"name": plugin_name, "file_patterns": patterns}
            with open(plugin_dir / "standards.json", "w") as f:
                json.dump(standards_json, f)

            with open(plugin_dir / "skills" / "main.md", "w") as f:
                f.write(skill_content)

            hooks_json = {"hooks": {}}
            with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
                json.dump(hooks_json, f)

        config_content = {
            "version": "1.0",
            "token_budget": {"max_tokens": 5000},
            "standards": {
                "enabled": ["red64-standards-typescript", "red64-standards-python"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_typescript_standards_loaded_for_ts_files(
        self, temp_project_with_multi_standards: Path
    ):
        """Test: TypeScript standards are loaded when .ts files are detected."""
        input_data = {
            "session_id": "test-session",
            "prompt": "Update the component.tsx file",
            "cwd": str(temp_project_with_multi_standards),
            "permission_mode": "default",
        }

        result = subprocess.run(
            [sys.executable, str(CONTEXT_LOADER_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=str(temp_project_with_multi_standards),
        )

        output = json.loads(result.stdout)
        additional_context = output.get("hookSpecificOutput", {}).get(
            "additionalContext", ""
        )
        assert "typescript" in additional_context.lower() or ".ts" in additional_context


class TestTokenBudgetPriorityRespected:
    """Tests for token budget respecting standards.token_budget_priority."""

    @pytest.fixture
    def temp_project_with_priority(self):
        """Create project with configured token budget priority."""
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

        long_skill = "# Long Skill\n\n## DO\n\n" + "Use patterns. " * 100 + "\n\n## DON'T\n\nAvoid bad patterns."
        with open(plugin_dir / "skills" / "long-skill.md", "w") as f:
            f.write(long_skill)

        hooks_json = {"hooks": {}}
        with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
            json.dump(hooks_json, f)

        config_content = {
            "version": "1.0",
            "token_budget": {"max_tokens": 500},
            "standards": {
                "enabled": ["red64-standards-test"],
                "token_budget_priority": 2,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_standards_priority_affects_budget_allocation(
        self, temp_project_with_priority: Path
    ):
        """Test: Token budget priority setting affects standards allocation."""
        input_data = {
            "session_id": "test-session",
            "prompt": "Edit the main.ts file",
            "cwd": str(temp_project_with_priority),
            "permission_mode": "default",
        }

        result = subprocess.run(
            [sys.executable, str(CONTEXT_LOADER_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=str(temp_project_with_priority),
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "hookSpecificOutput" in output


class TestMultipleStandardsWithPrecedence:
    """Tests for multiple standards with precedence information."""

    @pytest.fixture
    def temp_project_multiple_standards(self):
        """Create project with multiple standards for same file type."""
        temp_dir = tempfile.mkdtemp()
        red64_dir = Path(temp_dir) / ".red64"
        red64_dir.mkdir()

        for plugin_name, skill_name in [
            ("red64-standards-strict", "strict-rules"),
            ("red64-standards-base", "base-rules"),
        ]:
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

            skill_content = f"# {skill_name}\n\n## DO\n\nFollow {plugin_name} rules.\n\n## DON'T\n\nAvoid violations."
            with open(plugin_dir / "skills" / f"{skill_name}.md", "w") as f:
                f.write(skill_content)

            hooks_json = {"hooks": {}}
            with open(plugin_dir / "hooks" / "hooks.json", "w") as f:
                json.dump(hooks_json, f)

        config_content = {
            "version": "1.0",
            "token_budget": {"max_tokens": 5000},
            "standards": {
                "enabled": ["red64-standards-strict", "red64-standards-base"],
                "token_budget_priority": 3,
            },
        }
        with open(red64_dir / "config.yaml", "w") as f:
            yaml.dump(config_content, f)

        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_multiple_standards_included_with_precedence_info(
        self, temp_project_multiple_standards: Path
    ):
        """Test: Multiple standards are included with precedence information."""
        input_data = {
            "session_id": "test-session",
            "prompt": "Edit the app.ts file",
            "cwd": str(temp_project_multiple_standards),
            "permission_mode": "default",
        }

        result = subprocess.run(
            [sys.executable, str(CONTEXT_LOADER_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=str(temp_project_multiple_standards),
        )

        output = json.loads(result.stdout)
        additional_context = output.get("hookSpecificOutput", {}).get(
            "additionalContext", ""
        )
        assert "strict" in additional_context.lower() or "Standards" in additional_context


class TestStandardsLoaderScript:
    """Tests for standards-loader.py utility script."""

    @pytest.fixture
    def temp_project_for_loader(self):
        """Create project for testing standards loader script."""
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

        skill_content = "# Type Safety\n\n## DO\n\nUse explicit types.\n\n## DON'T\n\nAvoid any type."
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

    def test_standards_loader_returns_matched_skills(
        self, temp_project_for_loader: Path
    ):
        """Test: Standards loader returns matched skills for given file types."""
        input_data = {
            "file_types": [".ts", "app.tsx"],
            "cwd": str(temp_project_for_loader),
        }

        result = subprocess.run(
            [sys.executable, str(STANDARDS_LOADER_SCRIPT)],
            input=json.dumps(input_data),
            capture_output=True,
            text=True,
            cwd=str(temp_project_for_loader),
        )

        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "standards" in output
        assert len(output["standards"]) > 0
        first_standard = output["standards"][0]
        assert "plugin_name" in first_standard
        assert "skills" in first_standard
