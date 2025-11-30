#!/usr/bin/env python3
"""Roadmap parser script for detecting the current work item.

This script reads the product roadmap.md file and parses it to find
the first unchecked item (first [ ] found, not [x]). It extracts:
- Item number
- Item title
- Effort estimate
- Parent milestone

Handles edge cases: all items checked, malformed format, no file.
"""

import json
import re
import sys
from pathlib import Path
from typing import TypedDict


class ScriptInput(TypedDict):
    """Input schema for roadmap-parser script."""

    cwd: str


class CurrentItem(TypedDict):
    """Current roadmap item structure."""

    item_number: int
    item_title: str
    effort_estimate: str
    parent_milestone: str


class ScriptOutput(TypedDict):
    """Output schema for roadmap-parser script."""

    current_item: CurrentItem | None
    error: str | None


def find_roadmap_path(cwd: str) -> Path | None:
    """Find the roadmap.md file in the project.

    Args:
        cwd: Current working directory.

    Returns:
        Path to roadmap.md or None if not found.
    """
    roadmap_path = Path(cwd) / ".red64" / "product" / "roadmap.md"
    if roadmap_path.exists():
        return roadmap_path
    return None


def parse_effort_estimate(line: str) -> str:
    """Extract effort estimate from a roadmap line.

    Args:
        line: The roadmap item line.

    Returns:
        Effort estimate (XS, S, M, L, XL) or empty string if not found.
    """
    match = re.search(r"`(XS|S|M|L|XL)`", line)
    if match:
        return match.group(1)
    return ""


def parse_item_title(line: str) -> str:
    """Extract item title from a roadmap line.

    Args:
        line: The roadmap item line.

    Returns:
        The item title without checkbox, number, or effort estimate.
    """
    match = re.match(r"\d+\.\s*\[\s*[xX]?\s*\]\s*(.+)", line)
    if match:
        title = match.group(1).strip()
        title = re.sub(r"\s*--\s*.*$", "", title)
        title = re.sub(r"\s*`(XS|S|M|L|XL)`\s*$", "", title)
        return title.strip()
    return ""


def parse_item_number(line: str) -> int:
    """Extract item number from a roadmap line.

    Args:
        line: The roadmap item line.

    Returns:
        The item number, or 0 if not found.
    """
    match = re.match(r"(\d+)\.\s*\[", line)
    if match:
        return int(match.group(1))
    return 0


def find_current_milestone(content: str, item_line_number: int) -> str:
    """Find the parent milestone for a given item.

    Args:
        content: The full roadmap content.
        item_line_number: Line number of the current item.

    Returns:
        The milestone name, or empty string if not found.
    """
    lines = content.split("\n")
    current_milestone = ""

    for i, line in enumerate(lines):
        if i >= item_line_number:
            break
        if line.startswith("## "):
            milestone_text = line[3:].strip()
            milestone_text = re.sub(r"^Milestone\s+\d+:\s*", "", milestone_text)
            current_milestone = milestone_text

    return current_milestone


def parse_roadmap(roadmap_path: Path) -> tuple[CurrentItem | None, str | None]:
    """Parse roadmap.md to find the first unchecked item.

    Args:
        roadmap_path: Path to the roadmap.md file.

    Returns:
        Tuple of (CurrentItem or None, error message or None).
    """
    try:
        content = roadmap_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return None, f"Error reading roadmap: {str(e)}"

    if not content.strip():
        return None, None

    lines = content.split("\n")
    unchecked_pattern = re.compile(r"^\d+\.\s*\[\s*\]")

    for line_number, line in enumerate(lines):
        line = line.strip()
        if unchecked_pattern.match(line):
            item_number = parse_item_number(line)
            item_title = parse_item_title(line)
            effort_estimate = parse_effort_estimate(line)
            parent_milestone = find_current_milestone(content, line_number)

            if item_number == 0 or not item_title:
                return None, "Malformed roadmap item format"

            return {
                "item_number": item_number,
                "item_title": item_title,
                "effort_estimate": effort_estimate,
                "parent_milestone": parent_milestone,
            }, None

    return None, None


def main() -> int:
    """Main entry point for the roadmap parser script.

    Reads roadmap.md and finds the first unchecked item.
    Returns JSON with current_item field.

    Returns:
        Exit code: 0 for success.
    """
    try:
        input_data: ScriptInput = json.load(sys.stdin)
    except json.JSONDecodeError:
        output: ScriptOutput = {"current_item": None, "error": None}
        print(json.dumps(output))
        return 0

    cwd = input_data.get("cwd", "")

    roadmap_path = find_roadmap_path(cwd)
    if roadmap_path is None:
        output: ScriptOutput = {"current_item": None, "error": None}
        print(json.dumps(output))
        return 0

    current_item, error = parse_roadmap(roadmap_path)

    output: ScriptOutput = {"current_item": current_item, "error": error}
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
