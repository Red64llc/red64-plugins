#!/usr/bin/env python3
"""Product context orchestrator script.

This script orchestrates mission-summarizer.py and roadmap-parser.py
to generate a combined product context. It formats the output as a
Markdown block with "Product Context" header, including:
- Mission-lite summary
- Current roadmap item

Handles failures gracefully with partial output if one script fails.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import TypedDict


class ScriptInput(TypedDict):
    """Input schema for product-context script."""

    cwd: str


class MissionLite(TypedDict):
    """Condensed mission summary structure."""

    pitch: str
    problem: str
    key_features: list[str]


class CurrentItem(TypedDict):
    """Current roadmap item structure."""

    item_number: int
    item_title: str
    effort_estimate: str
    parent_milestone: str


class ScriptOutput(TypedDict):
    """Output schema for product-context script."""

    product_context: str


SCRIPTS_DIR = Path(__file__).parent


def run_sub_script(script_name: str, cwd: str) -> dict | None:
    """Run a sub-script and capture its JSON output.

    Args:
        script_name: Name of the script file.
        cwd: Current working directory to pass to the script.

    Returns:
        Parsed JSON output from the script, or None on failure.
    """
    script_path = SCRIPTS_DIR / script_name

    if not script_path.exists():
        return None

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps({"cwd": cwd}),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return None

        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return None


def get_mission_lite(cwd: str) -> MissionLite | None:
    """Get mission-lite summary from mission-summarizer.py.

    Args:
        cwd: Current working directory.

    Returns:
        MissionLite dict or None if unavailable.
    """
    result = run_sub_script("mission-summarizer.py", cwd)
    if result and result.get("mission_lite"):
        return result["mission_lite"]
    return None


def get_current_item(cwd: str) -> CurrentItem | None:
    """Get current roadmap item from roadmap-parser.py.

    Args:
        cwd: Current working directory.

    Returns:
        CurrentItem dict or None if unavailable.
    """
    result = run_sub_script("roadmap-parser.py", cwd)
    if result and result.get("current_item"):
        return result["current_item"]
    return None


def format_mission_section(mission_lite: MissionLite) -> list[str]:
    """Format mission-lite as markdown lines.

    Args:
        mission_lite: The mission-lite summary.

    Returns:
        List of markdown lines.
    """
    lines: list[str] = []

    lines.append("### Product Mission")
    lines.append("")

    if mission_lite.get("pitch"):
        lines.append(f"**Pitch:** {mission_lite['pitch']}")

    if mission_lite.get("problem"):
        lines.append(f"**Problem:** {mission_lite['problem']}")

    if mission_lite.get("key_features"):
        lines.append("")
        lines.append("**Key Features:**")
        for feature in mission_lite["key_features"]:
            lines.append(f"- {feature}")

    return lines


def format_roadmap_section(current_item: CurrentItem) -> list[str]:
    """Format current roadmap item as markdown lines.

    Args:
        current_item: The current roadmap item.

    Returns:
        List of markdown lines.
    """
    lines: list[str] = []

    lines.append("### Current Work Item")
    lines.append("")

    milestone = current_item.get("parent_milestone", "")
    if milestone:
        lines.append(f"**Milestone:** {milestone}")

    item_num = current_item.get("item_number", 0)
    title = current_item.get("item_title", "")
    effort = current_item.get("effort_estimate", "")

    if title:
        effort_str = f" ({effort})" if effort else ""
        lines.append(f"**Item {item_num}:** {title}{effort_str}")

    return lines


def format_product_context(
    mission_lite: MissionLite | None,
    current_item: CurrentItem | None,
) -> str:
    """Format the combined product context as markdown.

    Args:
        mission_lite: Mission-lite summary or None.
        current_item: Current roadmap item or None.

    Returns:
        Formatted markdown string.
    """
    lines: list[str] = []

    lines.append("## Product Context")
    lines.append("")

    if mission_lite is None and current_item is None:
        lines.append("*No product context available. Run `/red64:plan-mission` and `/red64:plan-roadmap` to set up product planning.*")
        return "\n".join(lines)

    if mission_lite:
        lines.extend(format_mission_section(mission_lite))
        lines.append("")

    if current_item:
        lines.extend(format_roadmap_section(current_item))

    return "\n".join(lines)


def main() -> int:
    """Main entry point for the product context script.

    Orchestrates mission-summarizer.py and roadmap-parser.py to generate
    combined product context formatted as markdown.

    Returns:
        Exit code: 0 for success.
    """
    try:
        input_data: ScriptInput = json.load(sys.stdin)
    except json.JSONDecodeError:
        output: ScriptOutput = {"product_context": ""}
        print(json.dumps(output))
        return 0

    cwd = input_data.get("cwd", "")

    mission_lite = get_mission_lite(cwd)
    current_item = get_current_item(cwd)

    product_context = format_product_context(mission_lite, current_item)

    output: ScriptOutput = {"product_context": product_context}
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
