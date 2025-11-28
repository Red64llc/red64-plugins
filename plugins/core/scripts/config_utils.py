"""Configuration utilities for loading and validating .red64/config.yaml.

Provides functions to load, validate, and access Red64 configuration.
"""

from pathlib import Path
from typing import Any

import yaml

from config_schema import (
    Red64Config,
    DEFAULT_MAX_TOKENS,
    get_default_config,
)


class ConfigNotFoundError(Exception):
    """Raised when .red64/config.yaml is not found."""

    pass


class ConfigMalformedError(Exception):
    """Raised when config.yaml contains invalid data."""

    pass


def find_config_path(start_path: str | Path | None = None) -> Path:
    """Find the .red64/config.yaml file starting from the given path.

    Searches upward through parent directories until config is found
    or root is reached.

    Args:
        start_path: Starting directory for search. Defaults to current directory.

    Returns:
        Path to the config.yaml file.

    Raises:
        ConfigNotFoundError: If config file is not found.
    """
    if start_path is None:
        start_path = Path.cwd()
    else:
        start_path = Path(start_path)

    current = start_path.resolve()
    root = Path(current.anchor)

    while current != root:
        config_path = current / ".red64" / "config.yaml"
        if config_path.exists():
            return config_path
        current = current.parent

    config_path = root / ".red64" / "config.yaml"
    if config_path.exists():
        return config_path

    raise ConfigNotFoundError(
        f"Config not found. Run /red64:init to initialize your project."
    )


def load_config(config_path: str | Path) -> Red64Config:
    """Load and validate configuration from the specified path.

    Args:
        config_path: Path to the config.yaml file.

    Returns:
        Validated Red64Config object.

    Raises:
        ConfigNotFoundError: If config file does not exist.
        ConfigMalformedError: If config file is invalid YAML or missing fields.
    """
    path = Path(config_path)

    if not path.exists():
        raise ConfigNotFoundError(
            f"Config not found at {config_path}. Run /red64:init to initialize."
        )

    try:
        with open(path) as f:
            config_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigMalformedError(f"Invalid YAML in config file: {e}")

    if config_data is None:
        raise ConfigMalformedError("Config file is empty.")

    if not isinstance(config_data, dict):
        raise ConfigMalformedError("Config file must contain a YAML mapping.")

    return merge_with_defaults(config_data)


def merge_with_defaults(config_data: dict[str, Any]) -> Red64Config:
    """Merge loaded config with default values for missing fields.

    Args:
        config_data: Partially loaded configuration.

    Returns:
        Complete Red64Config with defaults applied.
    """
    defaults = get_default_config()

    merged: dict[str, Any] = {}

    merged["version"] = config_data.get("version", defaults["version"])

    if "token_budget" in config_data:
        token_budget = config_data["token_budget"]
        merged["token_budget"] = {
            "max_tokens": token_budget.get(
                "max_tokens", defaults["token_budget"]["max_tokens"]
            ),
            "overflow_behavior": {
                "truncate": token_budget.get("overflow_behavior", {}).get(
                    "truncate",
                    defaults["token_budget"]["overflow_behavior"]["truncate"],
                ),
                "exclude": token_budget.get("overflow_behavior", {}).get(
                    "exclude",
                    defaults["token_budget"]["overflow_behavior"]["exclude"],
                ),
                "summary": token_budget.get("overflow_behavior", {}).get(
                    "summary",
                    defaults["token_budget"]["overflow_behavior"]["summary"],
                ),
            },
        }
    else:
        merged["token_budget"] = defaults["token_budget"]

    if "context_loader" in config_data:
        context_loader = config_data["context_loader"]
        merged["context_loader"] = {
            "enabled": context_loader.get(
                "enabled", defaults["context_loader"]["enabled"]
            ),
            "task_detection": context_loader.get(
                "task_detection", defaults["context_loader"]["task_detection"]
            ),
            "file_type_detection": context_loader.get(
                "file_type_detection",
                defaults["context_loader"]["file_type_detection"],
            ),
        }
    else:
        merged["context_loader"] = defaults["context_loader"]

    if "priorities" in config_data:
        priorities = config_data["priorities"]
        merged["priorities"] = {
            "product_mission": priorities.get(
                "product_mission", defaults["priorities"]["product_mission"]
            ),
            "current_spec": priorities.get(
                "current_spec", defaults["priorities"]["current_spec"]
            ),
            "relevant_standards": priorities.get(
                "relevant_standards", defaults["priorities"]["relevant_standards"]
            ),
            "tech_stack": priorities.get(
                "tech_stack", defaults["priorities"]["tech_stack"]
            ),
            "roadmap": priorities.get("roadmap", defaults["priorities"]["roadmap"]),
        }
    else:
        merged["priorities"] = defaults["priorities"]

    if "features" in config_data:
        features = config_data["features"]
        merged["features"] = {
            "standards_injection": features.get(
                "standards_injection", defaults["features"]["standards_injection"]
            ),
            "multi_agent": features.get(
                "multi_agent", defaults["features"]["multi_agent"]
            ),
            "metrics": features.get("metrics", defaults["features"]["metrics"]),
        }
    else:
        merged["features"] = defaults["features"]

    return merged  # type: ignore[return-value]


def get_token_budget(config: Red64Config) -> int:
    """Extract the token budget from configuration.

    Args:
        config: Loaded Red64 configuration.

    Returns:
        Maximum tokens allowed, defaulting to DEFAULT_MAX_TOKENS if not set.
    """
    return config.get("token_budget", {}).get("max_tokens", DEFAULT_MAX_TOKENS)


def get_overflow_behavior(config: Red64Config) -> dict[str, bool]:
    """Extract overflow behavior settings from configuration.

    Args:
        config: Loaded Red64 configuration.

    Returns:
        Dictionary with truncate, exclude, and summary flags.
    """
    default_behavior = {
        "truncate": True,
        "exclude": True,
        "summary": True,
    }

    token_budget = config.get("token_budget", {})
    return token_budget.get("overflow_behavior", default_behavior)
