#!/usr/bin/env python3
"""Mission summarizer script for extracting condensed mission context.

This script reads the product mission.md file and extracts a condensed
summary using rule-based extraction (not LLM). It extracts:
- First sentence from Pitch section
- First sentence from Problem section
- Bulleted list from Key Features section

Target summary length: 150-300 tokens.
"""

import json
import re
import sys
from pathlib import Path
from typing import TypedDict


class ScriptInput(TypedDict):
    """Input schema for mission-summarizer script."""

    cwd: str


class MissionLite(TypedDict):
    """Condensed mission summary structure."""

    pitch: str
    problem: str
    key_features: list[str]


class ScriptOutput(TypedDict):
    """Output schema for mission-summarizer script."""

    mission_lite: MissionLite | None


def find_mission_path(cwd: str) -> Path | None:
    """Find the mission.md file in the project.

    Args:
        cwd: Current working directory.

    Returns:
        Path to mission.md or None if not found.
    """
    mission_path = Path(cwd) / ".red64" / "product" / "mission.md"
    if mission_path.exists():
        return mission_path
    return None


def extract_first_sentence(text: str) -> str:
    """Extract the first sentence from text.

    Args:
        text: The text to extract from.

    Returns:
        The first sentence, or empty string if none found.
    """
    text = text.strip()
    if not text:
        return ""

    match = re.search(r"^[^.!?]*[.!?]", text)
    if match:
        return match.group(0).strip()

    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("-"):
            return line

    return text[:200] if len(text) > 200 else text


def extract_section_content(content: str, section_name: str) -> str:
    """Extract content from a specific markdown section.

    Args:
        content: The full markdown content.
        section_name: Name of the section to extract (e.g., "Pitch").

    Returns:
        The content of the section, or empty string if not found.
    """
    pattern = rf"##\s*(?:The\s+)?{re.escape(section_name)}\s*\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

    if match:
        section_content = match.group(1).strip()
        lines = []
        for line in section_content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("###"):
                continue
            if stripped.startswith("<!--") and stripped.endswith("-->"):
                continue
            if stripped:
                lines.append(stripped)
        return "\n".join(lines)

    return ""


def extract_key_features(content: str) -> list[str]:
    """Extract key features as a list from the Key Features section.

    Args:
        content: The full markdown content.

    Returns:
        List of feature descriptions.
    """
    features: list[str] = []

    section_content = extract_section_content(content, "Key Features")
    if not section_content:
        return features

    for line in section_content.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            feature_text = line[2:].strip()
            # Pattern: **Feature Name:** description (colon inside bold)
            match = re.match(r"\*\*(.+?):\*\*\s*(.*)", feature_text)
            if match:
                feature_name = match.group(1).strip()
                features.append(feature_name)
            # Pattern: **Feature Name**: description (colon outside bold)
            elif feature_text.startswith("**"):
                match = re.match(r"\*\*([^*]+)\*\*:\s*(.*)", feature_text)
                if match:
                    feature_name = match.group(1).strip()
                    features.append(feature_name)
                else:
                    features.append(feature_text[:100])
            else:
                features.append(feature_text[:100])

    return features[:10]


def extract_pitch_summary(content: str) -> str:
    """Extract pitch summary from the Pitch section.

    Args:
        content: The full markdown content.

    Returns:
        First sentence from pitch section.
    """
    section_content = extract_section_content(content, "Pitch")
    if not section_content:
        return ""

    for line in section_content.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("**Tagline"):
            continue
        sentence = extract_first_sentence(line)
        if sentence:
            sentence = re.sub(r"\*\*([^*]+)\*\*", r"\1", sentence)
            return sentence

    return ""


def extract_problem_summary(content: str) -> str:
    """Extract problem summary from the Problem section.

    Args:
        content: The full markdown content.

    Returns:
        First sentence from problem section.
    """
    section_content = extract_section_content(content, "Problem")
    if not section_content:
        return ""

    for line in section_content.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("**") and line.endswith("**"):
            continue
        if line.startswith("-"):
            continue

        sentence = extract_first_sentence(line)
        if sentence:
            return sentence

    return ""


def summarize_mission(mission_path: Path) -> MissionLite | None:
    """Extract condensed mission summary from mission.md.

    Args:
        mission_path: Path to the mission.md file.

    Returns:
        MissionLite with extracted summaries, or None on error.
    """
    try:
        content = mission_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    if not content.strip():
        return None

    pitch = extract_pitch_summary(content)
    problem = extract_problem_summary(content)
    key_features = extract_key_features(content)

    if not pitch and not problem and not key_features:
        return None

    return {
        "pitch": pitch,
        "problem": problem,
        "key_features": key_features,
    }


def main() -> int:
    """Main entry point for the mission summarizer script.

    Reads mission.md and extracts a condensed summary using rule-based
    extraction. Returns JSON with mission_lite field.

    Returns:
        Exit code: 0 for success.
    """
    try:
        input_data: ScriptInput = json.load(sys.stdin)
    except json.JSONDecodeError:
        output: ScriptOutput = {"mission_lite": None}
        print(json.dumps(output))
        return 0

    cwd = input_data.get("cwd", "")

    mission_path = find_mission_path(cwd)
    if mission_path is None:
        output: ScriptOutput = {"mission_lite": None}
        print(json.dumps(output))
        return 0

    mission_lite = summarize_mission(mission_path)

    output: ScriptOutput = {"mission_lite": mission_lite}
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
