"""Tests for context processing scripts.

Tests cover:
- Mission-summarizer extracts first sentence from Pitch section
- Mission-summarizer extracts first sentence from Problem section
- Mission-summarizer extracts Key Features as bullet list
- Roadmap-parser returns first unchecked [ ] item
- Roadmap-parser returns null when all items checked
- Roadmap-parser handles missing file gracefully
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
MISSION_SUMMARIZER = SCRIPTS_DIR / "mission-summarizer.py"
ROADMAP_PARSER = SCRIPTS_DIR / "roadmap-parser.py"
PRODUCT_CONTEXT = SCRIPTS_DIR / "product-context.py"


def create_temp_project(
    mission_content: str | None = None,
    roadmap_content: str | None = None,
) -> str:
    """Create a temporary project directory with optional product files.

    Args:
        mission_content: Content for mission.md (None means no file).
        roadmap_content: Content for roadmap.md (None means no file).

    Returns:
        Path to the temporary project directory.
    """
    temp_dir = tempfile.mkdtemp()
    product_dir = Path(temp_dir) / ".red64" / "product"
    product_dir.mkdir(parents=True)

    if mission_content is not None:
        mission_path = product_dir / "mission.md"
        with open(mission_path, "w") as f:
            f.write(mission_content)

    if roadmap_content is not None:
        roadmap_path = product_dir / "roadmap.md"
        with open(roadmap_path, "w") as f:
            f.write(roadmap_content)

    return temp_dir


def run_script(
    script_path: Path,
    cwd: str,
) -> tuple[dict | None, int]:
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


class TestMissionSummarizer:
    """Test suite for mission-summarizer.py script."""

    def test_extracts_first_sentence_from_pitch_section(self):
        """Test: Mission-summarizer extracts first sentence from Pitch section.

        The script should extract the first sentence from the Pitch section
        to use as part of the mission-lite summary.
        """
        mission_content = """# Product Mission

## Pitch

**Red64** is a modular plugin framework for Claude Code. It helps teams adopt structured workflows. More details here.

## Vision Statement

Some vision content.
"""
        temp_dir = create_temp_project(mission_content=mission_content)

        output, exit_code = run_script(MISSION_SUMMARIZER, temp_dir)

        assert exit_code == 0
        assert output is not None
        assert "mission_lite" in output
        assert "Red64" in output["mission_lite"]["pitch"]

    def test_extracts_first_sentence_from_problem_section(self):
        """Test: Mission-summarizer extracts first sentence from Problem section.

        The script should extract the first sentence from the Problem section
        to capture the core problem being solved.
        """
        mission_content = """# Product Mission

## Pitch

Some pitch content.

## The Problem

### Enterprise AI Development is Unpredictable

AI coding assistants produce inconsistent results. More details about the problem. Additional context.
"""
        temp_dir = create_temp_project(mission_content=mission_content)

        output, exit_code = run_script(MISSION_SUMMARIZER, temp_dir)

        assert exit_code == 0
        assert output is not None
        assert "mission_lite" in output
        assert "inconsistent" in output["mission_lite"]["problem"].lower()

    def test_extracts_key_features_as_bullet_list(self):
        """Test: Mission-summarizer extracts Key Features as bullet list.

        The script should extract Key Features section items as a bullet list.
        """
        mission_content = """# Product Mission

## Pitch

Some pitch.

## Key Features

### Core Workflow Features
- **Product Planning:** Define mission, roadmap, and tech stack
- **Spec-Driven Development:** Shape requirements into specifications

### Standards Features
- **Composable Standards Plugins:** Install stack-specific standards
"""
        temp_dir = create_temp_project(mission_content=mission_content)

        output, exit_code = run_script(MISSION_SUMMARIZER, temp_dir)

        assert exit_code == 0
        assert output is not None
        assert "mission_lite" in output
        features = output["mission_lite"]["key_features"]
        assert isinstance(features, list)
        assert len(features) >= 2

    def test_handles_missing_file_gracefully(self):
        """Test: Mission-summarizer handles missing file gracefully.

        When mission.md does not exist, the script should return null
        without throwing an error.
        """
        temp_dir = create_temp_project(mission_content=None)

        output, exit_code = run_script(MISSION_SUMMARIZER, temp_dir)

        assert exit_code == 0
        assert output is not None
        assert output.get("mission_lite") is None


class TestRoadmapParser:
    """Test suite for roadmap-parser.py script."""

    def test_returns_first_unchecked_item(self):
        """Test: Roadmap-parser returns first unchecked [ ] item.

        The parser should find and return the first item with an unchecked
        checkbox ([ ]) in the roadmap.
        """
        roadmap_content = """# Product Roadmap

## Milestone 1: Core Foundation

1. [x] First completed item -- Description `S`
2. [x] Second completed item -- Description `M`
3. [ ] First unchecked item -- This is the current work `M`
4. [ ] Another unchecked item -- Description `S`
"""
        temp_dir = create_temp_project(roadmap_content=roadmap_content)

        output, exit_code = run_script(ROADMAP_PARSER, temp_dir)

        assert exit_code == 0
        assert output is not None
        assert "current_item" in output
        current = output["current_item"]
        assert current["item_number"] == 3
        assert "First unchecked item" in current["item_title"]
        assert current["effort_estimate"] == "M"
        assert "Core Foundation" in current["parent_milestone"]

    def test_returns_null_when_all_items_checked(self):
        """Test: Roadmap-parser returns null when all items checked.

        When all items in the roadmap are checked ([x]), the parser should
        return null for current_item.
        """
        roadmap_content = """# Product Roadmap

## Milestone 1: Core Foundation

1. [x] First completed item -- Description `S`
2. [x] Second completed item -- Description `M`
3. [x] Third completed item -- Description `L`
"""
        temp_dir = create_temp_project(roadmap_content=roadmap_content)

        output, exit_code = run_script(ROADMAP_PARSER, temp_dir)

        assert exit_code == 0
        assert output is not None
        assert output.get("current_item") is None

    def test_handles_missing_file_gracefully(self):
        """Test: Roadmap-parser handles missing file gracefully.

        When roadmap.md does not exist, the script should return null
        without throwing an error.
        """
        temp_dir = create_temp_project(roadmap_content=None)

        output, exit_code = run_script(ROADMAP_PARSER, temp_dir)

        assert exit_code == 0
        assert output is not None
        assert output.get("current_item") is None


class TestProductContext:
    """Test suite for product-context.py orchestrator script."""

    def test_combines_mission_and_roadmap_output(self):
        """Test: Product-context.py combines mission and roadmap output.

        The orchestrator should call both scripts and format the output
        as a Markdown block.
        """
        mission_content = """# Product Mission

## Pitch

**TestProduct** is an amazing tool. It helps developers.

## The Problem

Developers struggle with complexity. This is a big issue.

## Key Features

- **Feature One:** Does something useful
- **Feature Two:** Does something else
"""
        roadmap_content = """# Product Roadmap

## Milestone 1: Setup

1. [ ] Initial setup -- Get started `S`
"""
        temp_dir = create_temp_project(
            mission_content=mission_content,
            roadmap_content=roadmap_content,
        )

        output, exit_code = run_script(PRODUCT_CONTEXT, temp_dir)

        assert exit_code == 0
        assert output is not None
        assert "product_context" in output
        context = output["product_context"]
        assert "TestProduct" in context or "Initial setup" in context

    def test_handles_partial_failure_gracefully(self):
        """Test: Product-context.py handles partial failure gracefully.

        If one script fails (e.g., missing file), the orchestrator should
        still return partial output from the successful script.
        """
        roadmap_content = """# Product Roadmap

## Milestone 1: Setup

1. [ ] Initial setup -- Get started `S`
"""
        temp_dir = create_temp_project(
            mission_content=None,
            roadmap_content=roadmap_content,
        )

        output, exit_code = run_script(PRODUCT_CONTEXT, temp_dir)

        assert exit_code == 0
        assert output is not None
        assert "product_context" in output
