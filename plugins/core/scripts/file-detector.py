#!/usr/bin/env python3
"""File detector script for identifying file types in user prompts.

Detects file extensions, explicit filenames, and path references from
user prompts to help determine relevant context for the context loader.
"""

import json
import re
import sys
from typing import TypedDict


class FileDetectorInput(TypedDict):
    """Input schema for file detector."""

    prompt: str


class FileDetectorOutput(TypedDict):
    """Output schema for file detector."""

    file_types: list[str]


EXTENSION_KEYWORDS: dict[str, list[str]] = {
    ".py": ["python", "py", ".py"],
    ".ts": ["typescript", "ts", ".ts"],
    ".js": ["javascript", "js", ".js"],
    ".md": ["markdown", "md", ".md"],
    ".yaml": ["yaml", ".yaml", ".yml"],
    ".json": ["json", ".json"],
    ".html": ["html", ".html"],
    ".css": ["css", ".css"],
}

FILENAME_PATTERN = re.compile(
    r"\b([a-zA-Z0-9_-]+\.(?:py|ts|js|md|yaml|yml|json|html|css))\b"
)

PATH_PATTERN = re.compile(
    r"\b([a-zA-Z0-9_.-]+(?:/[a-zA-Z0-9_.-]+)+/?)\b"
)


def detect_extensions_from_keywords(prompt: str) -> list[str]:
    """Detect file extensions based on language/type keywords in prompt.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        List of detected file extensions.
    """
    prompt_lower = prompt.lower()
    detected: list[str] = []

    for extension, keywords in EXTENSION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                if extension not in detected:
                    detected.append(extension)
                break

    return detected


def detect_explicit_filenames(prompt: str) -> list[str]:
    """Detect explicit filenames mentioned in the prompt.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        List of detected filenames.
    """
    matches = FILENAME_PATTERN.findall(prompt)
    return list(set(matches))


def detect_path_references(prompt: str) -> list[str]:
    """Detect path references in the prompt.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        List of detected path references.
    """
    matches = PATH_PATTERN.findall(prompt)
    paths: list[str] = []

    for match in matches:
        if "/" in match:
            path = match if match.endswith("/") else match + "/"
            if any(c.isalpha() for c in match.split("/")[0]):
                paths.append(path)

    return list(set(paths))


def detect_file_types(prompt: str) -> list[str]:
    """Detect all file types, filenames, and paths from a prompt.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        List of all detected file types, filenames, and paths.
    """
    file_types: list[str] = []

    extensions = detect_extensions_from_keywords(prompt)
    file_types.extend(extensions)

    filenames = detect_explicit_filenames(prompt)
    file_types.extend(filenames)

    paths = detect_path_references(prompt)
    file_types.extend(paths)

    return file_types


def main() -> int:
    """Main entry point for file detector.

    Reads prompt from stdin JSON and outputs detected file types.

    Returns:
        Exit code: 0 for success, 2 for blocking errors.
    """
    try:
        input_data: FileDetectorInput = json.load(sys.stdin)
        prompt = input_data.get("prompt", "")

        file_types = detect_file_types(prompt)

        output: FileDetectorOutput = {"file_types": file_types}
        print(json.dumps(output))
        return 0

    except json.JSONDecodeError:
        error_output = {"file_types": [], "error": "Invalid JSON input"}
        print(json.dumps(error_output))
        return 2

    except Exception as e:
        error_output = {"file_types": [], "error": str(e)}
        print(json.dumps(error_output))
        return 2


if __name__ == "__main__":
    sys.exit(main())
