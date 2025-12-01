#!/usr/bin/env python3
"""Standards loader script for loading standards skills based on file types.

This script loads standards skills from enabled plugins based on detected
file types. It matches file types against standards.json patterns and
returns skill content for inclusion in context.
"""

import fnmatch
import json
import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).parent))

from config_utils import (
    find_config_path,
    load_config,
    ConfigNotFoundError,
    ConfigMalformedError,
)


class StandardsLoaderInput(TypedDict):
    """Input schema for standards loader."""

    file_types: list[str]
    cwd: str


class SkillInfo(TypedDict):
    """Information about a loaded skill."""

    name: str
    content: str


class StandardInfo(TypedDict):
    """Information about a matched standard plugin."""

    plugin_name: str
    skills: list[SkillInfo]
    priority: int


class StandardsLoaderOutput(TypedDict, total=False):
    """Output schema for standards loader."""

    standards: list[StandardInfo]
    precedence_note: str
    error: str


def get_plugins_dir(cwd: str) -> Path:
    """Determine the plugins directory path.

    Args:
        cwd: Current working directory.

    Returns:
        Path to the plugins directory.
    """
    return Path(cwd) / "plugins"


def load_standards_json(plugin_path: Path) -> dict:
    """Load standards.json from a plugin directory.

    Args:
        plugin_path: Path to the standards plugin directory.

    Returns:
        Parsed standards.json content or empty dict if not found.
    """
    standards_json_path = plugin_path / "standards.json"
    if standards_json_path.exists():
        try:
            with open(standards_json_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def get_file_patterns(standards_json: dict) -> list[str]:
    """Extract file patterns from standards.json.

    Args:
        standards_json: Parsed standards.json content.

    Returns:
        List of file glob patterns.
    """
    return standards_json.get("file_patterns", [])


def file_type_matches_patterns(file_type: str, patterns: list[str]) -> bool:
    """Check if a file type matches any of the glob patterns.

    Args:
        file_type: File type or filename to check (e.g., ".ts", "app.tsx").
        patterns: List of glob patterns to match against.

    Returns:
        True if file type matches any pattern, False otherwise.
    """
    for pattern in patterns:
        if file_type.startswith("."):
            test_filename = f"test{file_type}"
            if fnmatch.fnmatch(test_filename, pattern):
                return True
        else:
            if fnmatch.fnmatch(file_type, pattern):
                return True
            filename = Path(file_type).name
            if fnmatch.fnmatch(filename, pattern):
                return True
    return False


def load_skills_from_plugin(plugin_path: Path) -> list[SkillInfo]:
    """Load all skills from a standards plugin.

    Args:
        plugin_path: Path to the standards plugin directory.

    Returns:
        List of SkillInfo with name and content.
    """
    skills: list[SkillInfo] = []
    skills_dir = plugin_path / "skills"

    if not skills_dir.exists():
        return skills

    for skill_file in sorted(skills_dir.glob("*.md")):
        try:
            content = skill_file.read_text()
            skills.append({
                "name": skill_file.stem,
                "content": content,
            })
        except IOError:
            continue

    return skills


def find_matching_standards(
    file_types: list[str],
    enabled_standards: list[str],
    plugins_dir: Path,
) -> list[tuple[str, Path, int]]:
    """Find standards plugins that match the given file types.

    Args:
        file_types: List of file types detected from prompt.
        enabled_standards: List of enabled standard plugin names.
        plugins_dir: Path to the plugins directory.

    Returns:
        List of (plugin_name, plugin_path, priority_index) tuples for matching standards.
    """
    matching: list[tuple[str, Path, int]] = []

    for priority_index, standard_name in enumerate(enabled_standards):
        plugin_path = plugins_dir / standard_name
        if not plugin_path.exists():
            continue

        standards_json = load_standards_json(plugin_path)
        patterns = get_file_patterns(standards_json)

        for file_type in file_types:
            if file_type_matches_patterns(file_type, patterns):
                matching.append((standard_name, plugin_path, priority_index))
                break

    return matching


def load_standards_for_file_types(
    file_types: list[str],
    cwd: str,
) -> StandardsLoaderOutput:
    """Load standards skills for the given file types.

    Args:
        file_types: List of file types detected from prompt.
        cwd: Current working directory.

    Returns:
        StandardsLoaderOutput with matched standards and skills.
    """
    if not file_types:
        return {"standards": []}

    try:
        config_path = find_config_path(cwd)
        config = load_config(config_path)
    except (ConfigNotFoundError, ConfigMalformedError):
        return {"standards": []}

    enabled_standards = config.get("standards", {}).get("enabled", [])
    if not enabled_standards:
        return {"standards": []}

    plugins_dir = get_plugins_dir(cwd)
    matching_standards = find_matching_standards(
        file_types, enabled_standards, plugins_dir
    )

    if not matching_standards:
        return {"standards": []}

    standards: list[StandardInfo] = []
    for plugin_name, plugin_path, priority_index in matching_standards:
        skills = load_skills_from_plugin(plugin_path)
        if skills:
            standards.append({
                "plugin_name": plugin_name,
                "skills": skills,
                "priority": priority_index,
            })

    output: StandardsLoaderOutput = {"standards": standards}

    if len(standards) > 1:
        first_plugin = standards[0]["plugin_name"]
        output["precedence_note"] = (
            f"Multiple standards apply. {first_plugin} takes precedence."
        )

    return output


def main() -> int:
    """Main entry point for standards loader.

    Reads file types from stdin JSON and outputs matched standards skills.

    Returns:
        Exit code: 0 for success, 2 for blocking errors.
    """
    try:
        input_data: StandardsLoaderInput = json.load(sys.stdin)
        file_types = input_data.get("file_types", [])
        cwd = input_data.get("cwd", "")

        output = load_standards_for_file_types(file_types, cwd)
        print(json.dumps(output))
        return 0

    except json.JSONDecodeError:
        error_output: StandardsLoaderOutput = {
            "standards": [],
            "error": "Invalid JSON input",
        }
        print(json.dumps(error_output))
        return 2

    except Exception as e:
        error_output: StandardsLoaderOutput = {
            "standards": [],
            "error": str(e),
        }
        print(json.dumps(error_output))
        return 2


if __name__ == "__main__":
    sys.exit(main())
