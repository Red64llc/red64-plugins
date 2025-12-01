#!/usr/bin/env python3
"""Standards validator PreToolUse hook for enforcing coding standards.

This script is invoked on PreToolUse events to validate Edit/Write operations
against enabled coding standards. It analyzes the target file path to determine
applicable standards based on file extension and checks for DON'T pattern violations.
"""

import fnmatch
import json
import re
import sys
from pathlib import Path
from typing import TypedDict


class ToolInput(TypedDict, total=False):
    """Tool input schema for Edit/Write operations."""

    file_path: str
    content: str


class ValidatorInput(TypedDict, total=False):
    """Input schema for PreToolUse hook."""

    tool_name: str
    tool_input: ToolInput
    cwd: str
    plugins_dir: str


class ValidatorOutput(TypedDict, total=False):
    """Output schema for PreToolUse hook response."""

    decision: str
    reason: str
    suggestion: str


EDIT_WRITE_TOOLS = {"Edit", "Write"}

_skills_cache: dict[str, list[str]] = {}


def get_plugins_dir(cwd: str, plugins_dir: str | None = None) -> Path:
    """Determine the plugins directory path.

    Args:
        cwd: Current working directory.
        plugins_dir: Optional explicit plugins directory path.

    Returns:
        Path to the plugins directory.
    """
    if plugins_dir:
        return Path(plugins_dir)
    return Path(cwd) / "plugins"


def load_config(cwd: str) -> dict:
    """Load configuration from .red64/config.yaml.

    Args:
        cwd: Current working directory to search from.

    Returns:
        Loaded configuration dictionary or empty dict if not found.
    """
    try:
        import yaml

        config_path = Path(cwd) / ".red64" / "config.yaml"
        if config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}


def get_enabled_standards(config: dict) -> list[str]:
    """Extract enabled standards list from configuration.

    Args:
        config: Loaded configuration dictionary.

    Returns:
        List of enabled standard plugin names in priority order.
    """
    standards = config.get("standards", {})
    return standards.get("enabled", [])


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


def file_matches_patterns(file_path: str, patterns: list[str]) -> bool:
    """Check if a file path matches any of the glob patterns.

    Args:
        file_path: Path to the file being checked.
        patterns: List of glob patterns to match against.

    Returns:
        True if file matches any pattern, False otherwise.
    """
    file_name = Path(file_path).name
    return any(fnmatch.fnmatch(file_name, pattern) for pattern in patterns)


def extract_dont_section(skill_content: str) -> str:
    """Extract the DON'T section from a SKILL.md file.

    Args:
        skill_content: Full content of the SKILL.md file.

    Returns:
        Content of the DON'T section, or empty string if not found.
    """
    dont_pattern = re.compile(
        r"^##\s*DON'T\s*$",
        re.MULTILINE | re.IGNORECASE
    )
    match = dont_pattern.search(skill_content)
    if not match:
        return ""

    start_pos = match.end()
    next_h2_pattern = re.compile(r"^##\s+", re.MULTILINE)
    next_match = next_h2_pattern.search(skill_content, start_pos)

    if next_match:
        return skill_content[start_pos:next_match.start()].strip()
    return skill_content[start_pos:].strip()


def extract_code_examples(dont_section: str) -> list[str]:
    """Extract code examples from fenced code blocks in DON'T section.

    Args:
        dont_section: Content of the DON'T section.

    Returns:
        List of code example strings.
    """
    code_pattern = re.compile(r"```\w*\n(.*?)```", re.DOTALL)
    matches = code_pattern.findall(dont_section)
    return [match.strip() for match in matches if match.strip()]


def load_dont_patterns_from_plugin(plugin_path: Path) -> list[str]:
    """Load and parse DON'T patterns from all skills in a plugin.

    Args:
        plugin_path: Path to the standards plugin directory.

    Returns:
        List of DON'T pattern strings and code examples.
    """
    cache_key = str(plugin_path)
    if cache_key in _skills_cache:
        return _skills_cache[cache_key]

    patterns: list[str] = []
    skills_dir = plugin_path / "skills"

    if not skills_dir.exists():
        return patterns

    for skill_file in skills_dir.glob("*.md"):
        try:
            content = skill_file.read_text()
            dont_section = extract_dont_section(content)
            if dont_section:
                patterns.append(dont_section)
                code_examples = extract_code_examples(dont_section)
                patterns.extend(code_examples)
        except IOError:
            continue

    _skills_cache[cache_key] = patterns
    return patterns


def check_content_against_patterns(
    content: str,
    patterns: list[str],
    plugin_name: str
) -> ValidatorOutput | None:
    """Check content against DON'T patterns for violations.

    Args:
        content: Content being written/edited.
        patterns: List of DON'T patterns and code examples.
        plugin_name: Name of the standards plugin for error messages.

    Returns:
        ValidatorOutput with block decision if violation found, None otherwise.
    """
    content_lower = content.lower()

    violation_checks = [
        (": any", "any type usage", "Use explicit types instead of 'any'."),
        (": any =", "any type usage", "Use explicit types instead of 'any'."),
        (": any;", "any type usage", "Use explicit types instead of 'any'."),
        ("var ", "var keyword usage", "Use 'const' or 'let' instead of 'var'."),
        ("eval(", "eval() usage", "Avoid using eval() for security reasons."),
    ]

    for check_pattern, violation_name, suggestion in violation_checks:
        if check_pattern in content_lower:
            for pattern in patterns:
                pattern_lower = pattern.lower()
                if check_pattern.replace(" ", "") in pattern_lower.replace(" ", ""):
                    return {
                        "decision": "block",
                        "reason": f"Violates {plugin_name} standard: {violation_name}",
                        "suggestion": suggestion,
                    }

    for pattern in patterns:
        if _pattern_matches_content(pattern, content):
            short_pattern = pattern[:100] + "..." if len(pattern) > 100 else pattern
            return {
                "decision": "block",
                "reason": f"Violates {plugin_name} standard: matches DON'T pattern",
                "suggestion": f"Review the DON'T pattern: {short_pattern}",
            }

    return None


def _pattern_matches_content(pattern: str, content: str) -> bool:
    """Check if a DON'T pattern matches the content.

    Args:
        pattern: The DON'T pattern to check.
        content: The content being validated.

    Returns:
        True if pattern indicates a violation in content.
    """
    pattern_lower = pattern.lower()
    content_lower = content.lower()

    critical_patterns = [
        ("single-letter variable", r"\bconst [a-z] ="),
        ("hungarian notation", r"\b(str|arr|obj|int|bool)[A-Z]"),
    ]

    for pattern_name, regex_pattern in critical_patterns:
        if pattern_name in pattern_lower:
            if re.search(regex_pattern, content):
                return True

    return False


def find_applicable_standards(
    file_path: str,
    enabled_standards: list[str],
    plugins_dir: Path
) -> list[tuple[str, Path]]:
    """Find standards that apply to the given file.

    Args:
        file_path: Path to the file being edited/written.
        enabled_standards: List of enabled standard plugin names.
        plugins_dir: Path to the plugins directory.

    Returns:
        List of (plugin_name, plugin_path) tuples for applicable standards.
    """
    applicable: list[tuple[str, Path]] = []

    for standard_name in enabled_standards:
        plugin_path = plugins_dir / standard_name
        if not plugin_path.exists():
            continue

        standards_json = load_standards_json(plugin_path)
        patterns = get_file_patterns(standards_json)

        if file_matches_patterns(file_path, patterns):
            applicable.append((standard_name, plugin_path))

    return applicable


def validate_tool_use(input_data: ValidatorInput) -> ValidatorOutput:
    """Validate a tool use against enabled standards.

    Args:
        input_data: PreToolUse hook input data.

    Returns:
        ValidatorOutput with decision and optional reason/suggestion.
    """
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    cwd = input_data.get("cwd", "")

    if tool_name not in EDIT_WRITE_TOOLS:
        return {"decision": "allow"}

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return {"decision": "allow"}

    config = load_config(cwd)
    enabled_standards = get_enabled_standards(config)

    if not enabled_standards:
        return {"decision": "allow"}

    plugins_dir = get_plugins_dir(cwd, input_data.get("plugins_dir"))
    applicable_standards = find_applicable_standards(
        file_path, enabled_standards, plugins_dir
    )

    if not applicable_standards:
        return {"decision": "allow"}

    content = tool_input.get("content", "")
    if not content:
        return {"decision": "allow"}

    for plugin_name, plugin_path in applicable_standards:
        dont_patterns = load_dont_patterns_from_plugin(plugin_path)
        if not dont_patterns:
            continue

        violation = check_content_against_patterns(
            content, dont_patterns, plugin_name
        )
        if violation:
            return violation

    return {"decision": "allow"}


def main() -> int:
    """Main entry point for the standards validator hook.

    Reads JSON input from stdin, validates against enabled standards,
    and returns JSON output with decision.

    Returns:
        Exit code: 0 for success.
    """
    try:
        input_data: ValidatorInput = json.load(sys.stdin)
    except json.JSONDecodeError:
        output: ValidatorOutput = {"decision": "allow"}
        print(json.dumps(output))
        return 0

    output = validate_tool_use(input_data)
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
