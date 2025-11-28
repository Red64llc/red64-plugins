"""Configuration schema for .red64/config.yaml.

Defines the default configuration structure for Red64 projects.
"""

from typing import TypedDict


class OverflowBehavior(TypedDict):
    """Token budget overflow handling behavior."""

    truncate: bool
    exclude: bool
    summary: bool


class TokenBudget(TypedDict):
    """Token budget configuration section."""

    max_tokens: int
    overflow_behavior: OverflowBehavior


class ContextLoader(TypedDict):
    """Context loader configuration section."""

    enabled: bool
    task_detection: bool
    file_type_detection: bool


class Priorities(TypedDict):
    """Priority levels for context items (lower number = higher priority)."""

    product_mission: int
    current_spec: int
    relevant_standards: int
    tech_stack: int
    roadmap: int


class Features(TypedDict):
    """Feature flags for future features."""

    standards_injection: bool
    multi_agent: bool
    metrics: bool


class Red64Config(TypedDict):
    """Complete Red64 configuration schema."""

    version: str
    token_budget: TokenBudget
    context_loader: ContextLoader
    priorities: Priorities
    features: Features


def get_default_config() -> Red64Config:
    """Return the default configuration for new Red64 projects.

    Returns:
        Red64Config with default values as per specification.
    """
    return {
        "version": "1.0",
        "token_budget": {
            "max_tokens": 3000,
            "overflow_behavior": {
                "truncate": True,
                "exclude": True,
                "summary": True,
            },
        },
        "context_loader": {
            "enabled": True,
            "task_detection": True,
            "file_type_detection": True,
        },
        "priorities": {
            "product_mission": 1,
            "current_spec": 2,
            "relevant_standards": 3,
            "tech_stack": 4,
            "roadmap": 5,
        },
        "features": {
            "standards_injection": False,
            "multi_agent": False,
            "metrics": False,
        },
    }


SCHEMA_VERSION = "1.0"
DEFAULT_MAX_TOKENS = 3000
