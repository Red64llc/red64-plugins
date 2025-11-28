#!/usr/bin/env python3
"""Budget manager script for token budget management.

Manages token budget allocation for context items, implementing:
- Priority-based sorting (lower number = higher priority)
- Token estimation (4 chars per token)
- Three-tier overflow handling:
  1. Truncate lower-priority items
  2. Exclude items if still over budget
  3. Generate exclusion summary
"""

import json
import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).parent))

from config_utils import (
    load_config,
    get_token_budget,
    get_overflow_behavior,
    ConfigNotFoundError,
    ConfigMalformedError,
)
from config_schema import DEFAULT_MAX_TOKENS


class ContextItem(TypedDict):
    """Context item with content and priority."""

    name: str
    content: str
    priority: int


class BudgetManagerInput(TypedDict):
    """Input schema for budget manager."""

    context_items: list[ContextItem]
    config_path: str


class BudgetManagerOutput(TypedDict, total=False):
    """Output schema for budget manager."""

    selected_items: list[ContextItem]
    exclusion_summary: str


CHARS_PER_TOKEN = 4


def estimate_tokens(content: str) -> int:
    """Estimate token count for content using 4 chars per token.

    Args:
        content: Text content to estimate.

    Returns:
        Estimated number of tokens.
    """
    return len(content) // CHARS_PER_TOKEN


def sort_by_priority(items: list[ContextItem]) -> list[ContextItem]:
    """Sort context items by priority (lower number = higher priority).

    Args:
        items: List of context items.

    Returns:
        Sorted list with highest priority (lowest number) first.
    """
    return sorted(items, key=lambda x: x.get("priority", 999))


def truncate_content(content: str, max_tokens: int) -> str:
    """Truncate content to fit within token budget.

    Args:
        content: Content to truncate.
        max_tokens: Maximum tokens allowed.

    Returns:
        Truncated content.
    """
    max_chars = max_tokens * CHARS_PER_TOKEN
    if len(content) <= max_chars:
        return content
    return content[:max_chars] + "..."


def calculate_total_tokens(items: list[ContextItem]) -> int:
    """Calculate total token count for all items.

    Args:
        items: List of context items.

    Returns:
        Total estimated tokens.
    """
    return sum(estimate_tokens(item["content"]) for item in items)


def manage_budget(
    context_items: list[ContextItem],
    max_tokens: int,
    overflow_behavior: dict[str, bool],
) -> BudgetManagerOutput:
    """Manage token budget for context items.

    Implements three-tier overflow handling:
    1. Truncate lower-priority items
    2. Exclude items if still over budget
    3. Generate exclusion summary

    Args:
        context_items: List of context items to process.
        max_tokens: Maximum token budget.
        overflow_behavior: Dict with truncate, exclude, summary flags.

    Returns:
        BudgetManagerOutput with selected items and optional exclusion summary.
    """
    if not context_items:
        return {"selected_items": []}

    sorted_items = sort_by_priority(context_items)

    total_tokens = calculate_total_tokens(sorted_items)
    if total_tokens <= max_tokens:
        return {"selected_items": sorted_items}

    can_truncate = overflow_behavior.get("truncate", True)
    can_exclude = overflow_behavior.get("exclude", True)
    show_summary = overflow_behavior.get("summary", True)

    selected_items: list[ContextItem] = []
    excluded_items: list[str] = []
    used_tokens = 0

    for item in sorted_items:
        item_tokens = estimate_tokens(item["content"])

        if used_tokens + item_tokens <= max_tokens:
            selected_items.append(item.copy())
            used_tokens += item_tokens
            continue

        remaining_budget = max_tokens - used_tokens
        if can_truncate and remaining_budget > 0:
            truncated_content = truncate_content(item["content"], remaining_budget)
            truncated_tokens = estimate_tokens(truncated_content)

            if truncated_tokens > 10:
                truncated_item = item.copy()
                truncated_item["content"] = truncated_content
                selected_items.append(truncated_item)
                used_tokens += truncated_tokens
                continue

        if can_exclude:
            excluded_items.append(item["name"])
        else:
            if remaining_budget > 0:
                truncated_content = truncate_content(item["content"], remaining_budget)
                truncated_item = item.copy()
                truncated_item["content"] = truncated_content
                selected_items.append(truncated_item)
                used_tokens += estimate_tokens(truncated_content)

    output: BudgetManagerOutput = {"selected_items": selected_items}

    if excluded_items and show_summary:
        output["exclusion_summary"] = (
            f"Excluded {len(excluded_items)} item(s) due to budget: "
            f"{', '.join(excluded_items)}"
        )

    return output


def main() -> int:
    """Main entry point for budget manager script.

    Reads JSON input from stdin with context_items and config_path.
    Outputs JSON to stdout with selected_items and optional exclusion_summary.

    Returns:
        Exit code: 0 for success, 2 for blocking errors.
    """
    try:
        input_data: BudgetManagerInput = json.load(sys.stdin)
        context_items = input_data.get("context_items", [])
        config_path = input_data.get("config_path")

        max_tokens = DEFAULT_MAX_TOKENS
        overflow_behavior = {"truncate": True, "exclude": True, "summary": True}

        if config_path:
            try:
                config = load_config(config_path)
                max_tokens = get_token_budget(config)
                overflow_behavior = get_overflow_behavior(config)
            except (ConfigNotFoundError, ConfigMalformedError):
                pass

        output = manage_budget(context_items, max_tokens, overflow_behavior)
        print(json.dumps(output))
        return 0

    except json.JSONDecodeError:
        error_output: BudgetManagerOutput = {
            "selected_items": [],
            "exclusion_summary": "Error: Invalid JSON input",
        }
        print(json.dumps(error_output))
        return 2

    except Exception as e:
        error_output: BudgetManagerOutput = {
            "selected_items": [],
            "exclusion_summary": f"Error: {str(e)}",
        }
        print(json.dumps(error_output))
        return 2


if __name__ == "__main__":
    sys.exit(main())
