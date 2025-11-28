#!/usr/bin/env python3
"""Task detector script for classifying user prompts into task types.

Classifies user prompts into task categories using built-in keyword patterns.
Task categories: shape, write-spec, implement, review, test, debug, refactor.
"""

import json
import sys
from typing import TypedDict


class TaskDetectorInput(TypedDict):
    """Input schema for task detector."""

    prompt: str


class TaskDetectorOutput(TypedDict):
    """Output schema for task detector."""

    task_type: str


TASK_PATTERNS: dict[str, list[str]] = {
    "shape": [
        "requirements",
        "scope",
        "define",
        "plan",
        "outline",
        "architect",
        "design",
    ],
    "write-spec": [
        "spec",
        "specification",
        "document",
        "write spec",
        "write-spec",
        "writespec",
        "prd",
    ],
    "implement": [
        "implement",
        "build",
        "create",
        "code",
        "develop",
        "make",
        "add",
        "write",
    ],
    "review": [
        "review",
        "check",
        "audit",
        "inspect",
        "examine",
        "analyze",
        "look at",
    ],
    "test": [
        "test",
        "verify",
        "validate",
        "assert",
        "unit test",
        "integration test",
    ],
    "debug": [
        "debug",
        "fix",
        "error",
        "bug",
        "issue",
        "problem",
        "broken",
        "failing",
    ],
    "refactor": [
        "refactor",
        "restructure",
        "reorganize",
        "clean up",
        "cleanup",
        "improve",
        "optimize",
    ],
}

TASK_PRIORITY: list[str] = [
    "debug",
    "test",
    "review",
    "shape",
    "write-spec",
    "refactor",
    "implement",
]


def detect_task_type(prompt: str) -> str:
    """Detect the task type from the user prompt using keyword matching.

    Uses lowercase keyword search against built-in patterns.
    Returns the first matching task type based on priority order.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        The detected task type or 'unknown' if no patterns match.
    """
    prompt_lower = prompt.lower()

    for task_type in TASK_PRIORITY:
        keywords = TASK_PATTERNS[task_type]
        for keyword in keywords:
            if keyword in prompt_lower:
                return task_type

    return "unknown"


def main() -> int:
    """Main entry point for task detector script.

    Reads JSON input from stdin with prompt field.
    Outputs JSON to stdout with task_type field.

    Returns:
        Exit code: 0 for success.
    """
    try:
        input_data: TaskDetectorInput = json.load(sys.stdin)
        prompt = input_data.get("prompt", "")

        task_type = detect_task_type(prompt)

        output: TaskDetectorOutput = {"task_type": task_type}
        print(json.dumps(output))
        return 0
    except json.JSONDecodeError:
        output: TaskDetectorOutput = {"task_type": "unknown"}
        print(json.dumps(output))
        return 0


if __name__ == "__main__":
    sys.exit(main())
