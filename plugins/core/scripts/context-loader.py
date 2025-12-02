#!/usr/bin/env python3
"""Context loader main script for UserPromptSubmit hook.

This is the main entry point that orchestrates the context loading pipeline.
It validates configuration, chains to sub-scripts for task detection,
file detection, standards loading, budget management, and product context,
then returns structured context.
"""

import json
import subprocess
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


class HookInput(TypedDict):
    """Input schema for UserPromptSubmit hook."""

    session_id: str
    prompt: str
    cwd: str
    permission_mode: str


class TaskDetectorOutput(TypedDict):
    """Output schema from task-detector.py."""

    task_type: str


class FileDetectorOutput(TypedDict):
    """Output schema from file-detector.py."""

    file_types: list[str]


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
    """Output schema from standards-loader.py."""

    standards: list[StandardInfo]
    precedence_note: str
    error: str


class BudgetManagerOutput(TypedDict, total=False):
    """Output schema from budget-manager.py."""

    selected_items: list[dict]
    exclusion_summary: str


class ProductContextOutput(TypedDict):
    """Output schema from product-context.py."""

    product_context: str


class HookOutput(TypedDict):
    """Output schema for UserPromptSubmit hook response."""

    event: str
    hookSpecificOutput: dict


SCRIPTS_DIR = Path(__file__).parent


def run_sub_script(script_name: str, input_data: dict) -> dict:
    """Run a sub-script and capture its JSON output.

    Args:
        script_name: Name of the script file (e.g., 'task-detector.py').
        input_data: Dictionary to pass as JSON input via stdin.

    Returns:
        Parsed JSON output from the script.

    Raises:
        RuntimeError: If script fails or returns invalid JSON.
    """
    script_path = SCRIPTS_DIR / script_name

    result = subprocess.run(
        [sys.executable, str(script_path)],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 and result.returncode != 2:
        raise RuntimeError(f"Script {script_name} failed: {result.stderr}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Script {script_name} returned invalid JSON: {e}")


def detect_task(prompt: str) -> TaskDetectorOutput:
    """Run task-detector.py to classify the user prompt.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        TaskDetectorOutput with detected task_type.
    """
    return run_sub_script("task-detector.py", {"prompt": prompt})


def detect_files(prompt: str) -> FileDetectorOutput:
    """Run file-detector.py to identify file types in the prompt.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        FileDetectorOutput with list of detected file_types.
    """
    return run_sub_script("file-detector.py", {"prompt": prompt})


def load_standards(file_types: list[str], cwd: str) -> StandardsLoaderOutput:
    """Run standards-loader.py to load applicable standards skills.

    Args:
        file_types: List of detected file types from the prompt.
        cwd: Current working directory.

    Returns:
        StandardsLoaderOutput with matched standards and skills.
    """
    return run_sub_script(
        "standards-loader.py",
        {
            "file_types": file_types,
            "cwd": cwd,
        },
    )


def manage_budget(
    context_items: list[dict],
    config_path: str,
) -> BudgetManagerOutput:
    """Run budget-manager.py to manage token budget for context items.

    Args:
        context_items: List of context items with name, content, priority.
        config_path: Path to the config.yaml file.

    Returns:
        BudgetManagerOutput with selected_items and optional exclusion_summary.
    """
    return run_sub_script(
        "budget-manager.py",
        {
            "context_items": context_items,
            "config_path": config_path,
        },
    )


def get_product_context(cwd: str) -> str | None:
    """Run product-context.py to get product context.

    Args:
        cwd: Current working directory.

    Returns:
        Product context string or None if unavailable.
    """
    try:
        result = run_sub_script("product-context.py", {"cwd": cwd})
        product_context = result.get("product_context", "")
        if product_context and "No product context available" not in product_context:
            return product_context
        return None
    except RuntimeError:
        return None


def create_standards_context_items(
    standards_result: StandardsLoaderOutput,
    token_budget_priority: int,
) -> list[dict]:
    """Create context items from loaded standards for budget management.

    Args:
        standards_result: Output from standards-loader.py.
        token_budget_priority: Priority value for standards in token budget.

    Returns:
        List of context items with name, content, and priority.
    """
    context_items: list[dict] = []
    standards = standards_result.get("standards", [])

    if not standards:
        return context_items

    total_standards = len(standards)
    for idx, standard in enumerate(standards):
        plugin_name = standard.get("plugin_name", "unknown")
        skills = standard.get("skills", [])

        skill_contents: list[str] = []
        for skill in skills:
            skill_contents.append(skill.get("content", ""))

        combined_content = "\n\n".join(skill_contents)
        if combined_content:
            adjusted_priority = token_budget_priority + (idx / (total_standards + 1))
            context_items.append({
                "name": f"standards:{plugin_name}",
                "content": combined_content,
                "priority": adjusted_priority,
            })

    return context_items


def format_standards_context(
    standards_result: StandardsLoaderOutput,
    selected_items: list[dict],
) -> str:
    """Format standards skills for inclusion in context output.

    Args:
        standards_result: Output from standards-loader.py.
        selected_items: Items selected by budget manager.

    Returns:
        Formatted string with standards headers and content.
    """
    lines: list[str] = []
    standards = standards_result.get("standards", [])

    if not standards:
        return ""

    selected_names = {item.get("name", "") for item in selected_items}

    precedence_note = standards_result.get("precedence_note")
    if precedence_note:
        lines.append("")
        lines.append(f"*Note: {precedence_note}*")
        lines.append("")

    for standard in standards:
        plugin_name = standard.get("plugin_name", "unknown")
        item_name = f"standards:{plugin_name}"

        if item_name not in selected_names and selected_items:
            continue

        skills = standard.get("skills", [])
        if not skills:
            continue

        lines.append(f"## Standards: {plugin_name}")
        lines.append("")

        for skill in skills:
            content = skill.get("content", "")
            if content:
                lines.append(content)
                lines.append("")

    return "\n".join(lines).strip()


def format_additional_context(
    task_type: str,
    file_types: list[str],
    budget_result: BudgetManagerOutput,
    product_context: str | None = None,
    standards_context: str | None = None,
) -> str:
    """Format the additional context string for hook output.

    Args:
        task_type: Detected task type from task-detector.
        file_types: Detected file types from file-detector.
        budget_result: Result from budget-manager.
        product_context: Optional product context from product-context.py.
        standards_context: Optional standards context from standards-loader.py.

    Returns:
        Formatted context string.
    """
    lines: list[str] = []

    lines.append("## Red64 Context")
    lines.append("")
    lines.append(f"**Detected Task Type:** {task_type}")

    if file_types:
        lines.append(f"**Detected File Types:** {', '.join(file_types)}")

    if budget_result.get("exclusion_summary"):
        lines.append("")
        lines.append(f"*{budget_result['exclusion_summary']}*")

    if standards_context:
        lines.append("")
        lines.append(standards_context)

    if product_context:
        lines.append("")
        lines.append(product_context)

    return "\n".join(lines)


def create_error_output(message: str) -> HookOutput:
    """Create a hook output for error conditions.

    Args:
        message: Error message to include.

    Returns:
        HookOutput with error message in additionalContext.
    """
    return {
        "event": "UserPromptSubmit",
        "hookSpecificOutput": {
            "additionalContext": message,
        }
    }


def create_success_output(additional_context: str) -> HookOutput:
    """Create a hook output for successful execution.

    Args:
        additional_context: Context content to include.

    Returns:
        HookOutput with context in additionalContext.
    """
    return {
        "event": "UserPromptSubmit",
        "hookSpecificOutput": {
            "additionalContext": additional_context,
        }
    }


def main() -> int:
    """Main entry point for the context loader hook.

    Orchestrates the context loading pipeline:
    1. Read and validate JSON input from stdin
    2. Validate .red64/config.yaml presence and format
    3. Chain to sub-scripts for task/file detection
    4. Load applicable standards based on detected file types
    5. Manage token budget with standards included
    6. Get product context from product-context.py
    7. Return structured JSON with hookSpecificOutput.additionalContext

    Returns:
        Exit code: 0 for success, 2 for blocking errors.
    """
    try:
        input_data: HookInput = json.load(sys.stdin)
    except json.JSONDecodeError:
        output = create_error_output(
            "Error: Invalid JSON input. Please run /red64:init to set up your project."
        )
        print(json.dumps(output))
        return 2

    prompt = input_data.get("prompt", "")
    cwd = input_data.get("cwd", "")

    try:
        config_path = find_config_path(cwd)
        config = load_config(config_path)
    except ConfigNotFoundError:
        output = create_error_output(
            "Error: Red64 configuration not found. "
            "Please run /red64:init to initialize your project."
        )
        print(json.dumps(output))
        return 2
    except ConfigMalformedError as e:
        output = create_error_output(
            f"Error: Red64 configuration is malformed. {str(e)} "
            "Please run /red64:init to reinitialize your project."
        )
        print(json.dumps(output))
        return 2

    try:
        task_result = detect_task(prompt)
        task_type = task_result.get("task_type", "unknown")
    except RuntimeError:
        task_type = "unknown"

    try:
        file_result = detect_files(prompt)
        file_types = file_result.get("file_types", [])
    except RuntimeError:
        file_types = []

    standards_result: StandardsLoaderOutput = {"standards": []}
    standards_context_items: list[dict] = []
    token_budget_priority = config.get("standards", {}).get("token_budget_priority", 3)

    if file_types:
        try:
            standards_result = load_standards(file_types, cwd)
            standards_context_items = create_standards_context_items(
                standards_result, token_budget_priority
            )
        except RuntimeError:
            pass

    context_items: list[dict] = standards_context_items

    try:
        budget_result = manage_budget(context_items, str(config_path))
    except RuntimeError:
        budget_result = {"selected_items": context_items}

    selected_items = budget_result.get("selected_items", [])
    standards_context = format_standards_context(standards_result, selected_items)

    product_context = get_product_context(cwd)

    additional_context = format_additional_context(
        task_type,
        file_types,
        budget_result,
        product_context,
        standards_context,
    )

    output = create_success_output(additional_context)
    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
