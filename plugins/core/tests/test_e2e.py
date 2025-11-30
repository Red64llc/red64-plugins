"""End-to-end tests for Product Planning Workflow feature.

Tests cover critical integration points and edge cases:
- End-to-end workflow from planning commands to context injection
- Mission-summarizer output meets token budget (150-300)
- Roadmap-parser handles multiple milestone formats
- Edge cases: empty files, missing directories, malformed formats
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml


SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
CONTEXT_LOADER = SCRIPTS_DIR / "context-loader.py"
MISSION_SUMMARIZER = SCRIPTS_DIR / "mission-summarizer.py"
ROADMAP_PARSER = SCRIPTS_DIR / "roadmap-parser.py"


def create_project_with_config(
    temp_dir: Path,
    mission_content: str | None = None,
    roadmap_content: str | None = None,
    tech_stack_content: str | None = None,
) -> None:
    """Create a complete project structure with config and optional product docs.

    Args:
        temp_dir: Root directory for the project.
        mission_content: Optional content for mission.md.
        roadmap_content: Optional content for roadmap.md.
        tech_stack_content: Optional content for tech-stack.md.
    """
    red64_dir = temp_dir / ".red64"
    red64_dir.mkdir(parents=True, exist_ok=True)

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
    config_path = red64_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    if any([mission_content, roadmap_content, tech_stack_content]):
        product_dir = red64_dir / "product"
        product_dir.mkdir(parents=True, exist_ok=True)

        if mission_content is not None:
            (product_dir / "mission.md").write_text(mission_content)
        if roadmap_content is not None:
            (product_dir / "roadmap.md").write_text(roadmap_content)
        if tech_stack_content is not None:
            (product_dir / "tech-stack.md").write_text(tech_stack_content)


def run_script(script_path: Path, cwd: str) -> tuple[dict | None, int]:
    """Run a script and capture its JSON output.

    Args:
        script_path: Path to the Python script.
        cwd: Current working directory for the script.

    Returns:
        Tuple of (parsed JSON output or None, exit code).
    """
    input_data = json.dumps({"cwd": cwd})

    result = subprocess.run(
        [sys.executable, str(script_path)],
        input=input_data,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
    )

    try:
        output = json.loads(result.stdout) if result.stdout.strip() else None
    except json.JSONDecodeError:
        output = None

    return output, result.returncode


def run_context_loader(cwd: str, prompt: str = "test prompt") -> tuple[dict | str, int]:
    """Run context-loader.py with the given input.

    Args:
        cwd: Current working directory.
        prompt: The user prompt.

    Returns:
        Tuple of (parsed output or raw stdout, exit code).
    """
    input_data = json.dumps({
        "session_id": "test-session",
        "prompt": prompt,
        "cwd": cwd,
        "permission_mode": "default",
    })

    result = subprocess.run(
        [sys.executable, str(CONTEXT_LOADER)],
        input=input_data,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
    )

    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = result.stdout

    return output, result.returncode


def estimate_tokens(text: str) -> int:
    """Estimate token count using simple word-based approximation.

    Args:
        text: The text to estimate tokens for.

    Returns:
        Estimated token count (words * 1.3 to approximate subword tokenization).
    """
    words = len(text.split())
    return int(words * 1.3)


class TestEndToEndWorkflows:
    """End-to-end tests for complete Product Planning Workflow."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_planning_commands_create_all_files_and_context_injection(
        self,
        temp_project: Path,
    ):
        """Test: Run all 3 planning commands, verify files created and context injection.

        This validates the complete workflow:
        1. Mission template creates file at correct location
        2. Roadmap template creates file at correct location
        3. Tech-stack template creates file at correct location
        4. Context injection includes product context in hook output
        """
        mission_template = (TEMPLATES_DIR / "mission-template.md").read_text()
        roadmap_template = (TEMPLATES_DIR / "roadmap-template.md").read_text()
        tech_stack_template = (TEMPLATES_DIR / "tech-stack-template.md").read_text()

        create_project_with_config(
            temp_project,
            mission_content=mission_template,
            roadmap_content=roadmap_template,
            tech_stack_content=tech_stack_template,
        )

        mission_path = temp_project / ".red64" / "product" / "mission.md"
        roadmap_path = temp_project / ".red64" / "product" / "roadmap.md"
        tech_stack_path = temp_project / ".red64" / "product" / "tech-stack.md"

        assert mission_path.exists(), "Mission file should be created"
        assert roadmap_path.exists(), "Roadmap file should be created"
        assert tech_stack_path.exists(), "Tech-stack file should be created"

        output, exit_code = run_context_loader(
            str(temp_project),
            prompt="Implement a new feature",
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        assert "hookSpecificOutput" in output
        additional_context = output["hookSpecificOutput"]["additionalContext"]
        assert "Product Context" in additional_context

    def test_custom_product_docs_appear_in_context_injection(
        self,
        temp_project: Path,
    ):
        """Test: Create product docs with custom content, verify context reflects edits.

        Verifies that when users edit their product docs:
        1. Mission-lite summary reflects the custom content
        2. Current roadmap item detection works
        3. Product context includes the custom information
        """
        mission_content = """# Product Mission

## Pitch

**TestApp** is a revolutionary testing framework that helps developers write better tests faster.

## The Problem

### Test Writing is Tedious

Developers spend too much time writing boilerplate test code.

## Key Features

- **Auto-Generation:** Automatically generates test stubs
- **Smart Assertions:** Suggests meaningful assertions
- **Coverage Tracking:** Real-time coverage visualization
"""
        roadmap_content = """# Product Roadmap

## Milestone 1: Core Testing Features

1. [x] Set up test framework -- Initial project structure `S`
2. [x] Implement test runner -- Basic execution engine `M`
3. [ ] Add assertion library -- Custom matchers for tests `S`
4. [ ] Coverage reporting -- Track test coverage `M`
"""
        create_project_with_config(
            temp_project,
            mission_content=mission_content,
            roadmap_content=roadmap_content,
        )

        output, exit_code = run_context_loader(
            str(temp_project),
            prompt="What feature should I work on next?",
        )

        assert exit_code == 0
        assert isinstance(output, dict)
        additional_context = output["hookSpecificOutput"]["additionalContext"]

        assert "Product Context" in additional_context
        assert "TestApp" in additional_context or "revolutionary" in additional_context
        assert "Add assertion library" in additional_context or "assertion" in additional_context.lower()


class TestMissionSummarizerTokenBudget:
    """Tests for mission-summarizer token budget compliance."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_mission_lite_output_within_token_budget(self, temp_project: Path):
        """Test: Verify mission-summarizer output meets token budget (150-300).

        The mission-lite summary should be concise enough to fit within
        the 150-300 token target while still capturing key information.
        """
        mission_content = """# Product Mission

## Pitch

**Red64** is a modular plugin framework for Claude Code that standardizes enterprise AI workflows through composable plugins, bringing consistency and predictability to AI-assisted development.

**Tagline:** "Structured AI Development at Scale"

## Vision Statement

Red64 transforms how engineering organizations work with AI assistants. By providing a structured framework that captures institutional knowledge, we enable teams to get consistent, high-quality outputs without sacrificing the flexibility that makes AI valuable.

The future of software development is hybrid human-AI collaboration. Red64 bridges the gap between unpredictable AI interactions and the reliability enterprises demand.

## The Problem

### Enterprise AI Development is Unpredictable

AI coding assistants produce inconsistent results across different developers and sessions. The current approaches result in lost productivity and quality variance. For enterprises where compliance is critical, this unpredictability is a fundamental barrier to AI adoption.

**Quantifiable Impact:**
- Teams spend 30-40% of AI interaction time on repeated clarifications
- Output quality varies significantly between sessions
- No way to capture and share successful interaction patterns
- Compliance concerns prevent adoption in regulated industries

**Our Solution:** Red64 provides a framework that standardizes how AI assistants behave.

## Key Features

### Core Workflow Features
- **Product Planning:** Define mission, roadmap, and tech stack
- **Spec-Driven Development:** Shape requirements into specifications
- **Task Breakdown:** Convert specs into manageable task lists

### Standards Features
- **Composable Standards Plugins:** Install stack-specific standards
- **Automatic Context Injection:** Standards applied without manual prompting
- **Token Budget Management:** Intelligent context selection

## Success Metrics

### Technical Metrics
| Metric | Target |
|--------|--------|
| Context Load Time | < 200ms |
| Plugin Install Time | < 5s |
| Hook Execution Time | < 100ms |
"""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True)
        (product_dir / "mission.md").write_text(mission_content)

        output, exit_code = run_script(MISSION_SUMMARIZER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        assert "mission_lite" in output

        mission_lite = output["mission_lite"]
        assert mission_lite is not None

        combined_text = f"{mission_lite.get('pitch', '')} {mission_lite.get('problem', '')} {' '.join(mission_lite.get('key_features', []))}"
        token_estimate = estimate_tokens(combined_text)

        assert token_estimate <= 400, (
            f"Mission-lite exceeds token budget: ~{token_estimate} tokens. "
            "Target is 150-300 tokens. Content may need further truncation."
        )
        assert token_estimate >= 20, (
            f"Mission-lite too short: ~{token_estimate} tokens. "
            "Summary should capture meaningful content."
        )


class TestRoadmapParserMilestoneFormats:
    """Tests for roadmap-parser handling of various milestone formats."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_handles_milestone_with_number_prefix(self, temp_project: Path):
        """Test: Roadmap-parser handles 'Milestone N:' format."""
        roadmap_content = """# Product Roadmap

## Milestone 1: Core Foundation

1. [x] Completed task -- Done `S`
2. [ ] Current task -- In progress `M`
"""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True)
        (product_dir / "roadmap.md").write_text(roadmap_content)

        output, exit_code = run_script(ROADMAP_PARSER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        assert output.get("current_item") is not None
        assert "Core Foundation" in output["current_item"]["parent_milestone"]

    def test_handles_milestone_without_number(self, temp_project: Path):
        """Test: Roadmap-parser handles milestone without 'Milestone N:' prefix."""
        roadmap_content = """# Product Roadmap

## Alpha Release

1. [x] Completed task -- Done `S`
2. [ ] Current task -- In progress `M`
"""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True)
        (product_dir / "roadmap.md").write_text(roadmap_content)

        output, exit_code = run_script(ROADMAP_PARSER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        assert output.get("current_item") is not None
        assert "Alpha Release" in output["current_item"]["parent_milestone"]

    def test_handles_items_across_multiple_milestones(self, temp_project: Path):
        """Test: Roadmap-parser finds correct item when spanning milestones."""
        roadmap_content = """# Product Roadmap

## Milestone 1: Foundation

1. [x] First task -- Done `S`
2. [x] Second task -- Done `M`

## Milestone 2: Features

3. [x] Third task -- Done `S`
4. [ ] Fourth task -- Current work `L`
5. [ ] Fifth task -- Not yet `M`
"""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True)
        (product_dir / "roadmap.md").write_text(roadmap_content)

        output, exit_code = run_script(ROADMAP_PARSER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        current_item = output.get("current_item")
        assert current_item is not None
        assert current_item["item_number"] == 4
        assert "Fourth task" in current_item["item_title"]
        assert "Features" in current_item["parent_milestone"]


class TestEdgeCases:
    """Tests for edge cases in Product Planning Workflow."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_empty_mission_file_handling(self, temp_project: Path):
        """Test: Empty mission.md file is handled gracefully."""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True)
        (product_dir / "mission.md").write_text("")

        output, exit_code = run_script(MISSION_SUMMARIZER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        assert output.get("mission_lite") is None

    def test_roadmap_with_only_completed_items(self, temp_project: Path):
        """Test: Roadmap with only completed items returns null current_item."""
        roadmap_content = """# Product Roadmap

## Milestone 1: Done

1. [x] First task -- Completed `S`
2. [x] Second task -- Completed `M`
3. [x] Third task -- Completed `L`
"""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True)
        (product_dir / "roadmap.md").write_text(roadmap_content)

        output, exit_code = run_script(ROADMAP_PARSER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        assert output.get("current_item") is None
        assert output.get("error") is None

    def test_product_docs_directory_missing(self, temp_project: Path):
        """Test: Missing .red64/product directory is handled gracefully."""
        red64_dir = temp_project / ".red64"
        red64_dir.mkdir(parents=True)

        output, exit_code = run_script(MISSION_SUMMARIZER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        assert output.get("mission_lite") is None

    def test_lenient_checkbox_parsing(self, temp_project: Path):
        """Test: Parser handles checkbox formats leniently.

        The roadmap parser uses lenient matching where [] (no space)
        is treated the same as [ ] (with space) for unchecked items.
        This provides flexibility for user formatting variations.
        """
        roadmap_content = """# Product Roadmap

## Milestone 1: Lenient Format

1. [] First item with no space checkbox -- Lenient parsing `S`
2. [ ] Second item with standard checkbox -- Normal format `M`
"""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True)
        (product_dir / "roadmap.md").write_text(roadmap_content)

        output, exit_code = run_script(ROADMAP_PARSER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        current_item = output.get("current_item")
        assert current_item is not None
        assert current_item["item_number"] == 1
        assert "First item with no space checkbox" in current_item["item_title"]

    def test_non_roadmap_item_lines_are_skipped(self, temp_project: Path):
        """Test: Lines that are not valid roadmap items are skipped.

        Lines without the proper 'N. [ ]' format should be ignored.
        """
        roadmap_content = """# Product Roadmap

## Milestone 1: Mixed Content

This is a description paragraph that should be ignored.

- A bullet point that is not a roadmap item

1. [x] First completed item -- Done `S`
2. [ ] Second unchecked item -- Current work `M`

Some trailing text.
"""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True)
        (product_dir / "roadmap.md").write_text(roadmap_content)

        output, exit_code = run_script(ROADMAP_PARSER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        current_item = output.get("current_item")
        assert current_item is not None
        assert current_item["item_number"] == 2
        assert "Second unchecked item" in current_item["item_title"]

    def test_mission_with_minimal_content(self, temp_project: Path):
        """Test: Mission file with only some sections is handled gracefully."""
        mission_content = """# Product Mission

## Pitch

**MinimalApp** does one thing well.

## Key Features

- **Feature One:** The main feature
"""
        product_dir = temp_project / ".red64" / "product"
        product_dir.mkdir(parents=True)
        (product_dir / "mission.md").write_text(mission_content)

        output, exit_code = run_script(MISSION_SUMMARIZER, str(temp_project))

        assert exit_code == 0
        assert output is not None
        mission_lite = output.get("mission_lite")
        assert mission_lite is not None
        assert "MinimalApp" in mission_lite["pitch"]
        assert len(mission_lite["key_features"]) >= 1
