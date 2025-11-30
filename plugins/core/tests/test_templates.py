"""Tests for document template content quality.

Tests cover:
- Mission template has all required sections (Pitch, Vision, Problem, Users, Differentiators, Key Features, Success Metrics)
- Roadmap template enforces exact checklist format with effort estimates
- Tech-stack template has category-based organization
"""

import re
from pathlib import Path

import pytest


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def read_template(name: str) -> str:
    """Read a template file and return its content.

    Args:
        name: Template filename (e.g., "mission-template.md").

    Returns:
        Template file content as string.
    """
    template_path = TEMPLATES_DIR / name
    return template_path.read_text()


class TestMissionTemplate:
    """Test suite for mission template content quality."""

    def test_has_all_required_sections(self):
        """Test: Mission template has all required sections.

        The mission template must include these seven sections:
        - Pitch
        - Vision Statement (or Vision)
        - Problem
        - Users
        - Differentiators
        - Key Features
        - Success Metrics
        """
        content = read_template("mission-template.md")

        required_sections = [
            "Pitch",
            "Vision",
            "Problem",
            "Users",
            "Differentiators",
            "Key Features",
            "Success Metrics",
        ]

        for section in required_sections:
            pattern = rf"^##\s+.*{section}.*$"
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            assert match is not None, f"Missing required section: {section}"

    def test_has_html_comment_hints(self):
        """Test: Mission template includes HTML comment hints for guidance.

        Each major section should have HTML comments to guide users on
        what content to add.
        """
        content = read_template("mission-template.md")

        assert "<!--" in content, "Template should include HTML comment hints"
        assert "-->" in content, "Template should have properly closed HTML comments"

        comment_count = content.count("<!--")
        assert comment_count >= 5, f"Expected at least 5 HTML comment hints, found {comment_count}"

    def test_has_professional_example_content(self):
        """Test: Mission template uses professional example content.

        Template should not contain lorem ipsum or placeholder-only text.
        It should have realistic example structures.
        """
        content = read_template("mission-template.md")

        assert "lorem ipsum" not in content.lower(), "Template should not use lorem ipsum"
        assert "TODO" not in content, "Template should not have bare TODO markers"

        assert "target users" in content.lower() or "target" in content.lower()
        assert "metric" in content.lower()


class TestRoadmapTemplate:
    """Test suite for roadmap template format compliance."""

    def test_enforces_checklist_format(self):
        """Test: Roadmap template enforces exact checklist format.

        Each roadmap item must use numbered items with [ ] or [x] checkboxes.
        Format: N. [ ] Task description -- Explanation `EFFORT`
        """
        content = read_template("roadmap-template.md")

        checklist_pattern = r"^\d+\.\s+\[([ x])\]\s+.+"
        matches = re.findall(checklist_pattern, content, re.MULTILINE)

        assert len(matches) >= 5, f"Expected at least 5 checklist items, found {len(matches)}"

    def test_includes_effort_estimates(self):
        """Test: Roadmap template includes effort estimates on each item.

        Each checklist item should have an effort estimate in backticks:
        XS, S, M, L, or XL.
        """
        content = read_template("roadmap-template.md")

        item_pattern = r"^\d+\.\s+\[([ x])\]\s+.+"
        items = re.findall(item_pattern, content, re.MULTILINE)

        effort_pattern = r"`(XS|S|M|L|XL)`"
        effort_matches = re.findall(effort_pattern, content)

        assert len(effort_matches) >= len(items), (
            f"Each of the {len(items)} items should have an effort estimate, "
            f"but only found {len(effort_matches)} effort markers"
        )

    def test_has_multiple_milestones(self):
        """Test: Roadmap template provides 2-3 example milestones.

        Template should demonstrate the structure with multiple milestones.
        """
        content = read_template("roadmap-template.md")

        milestone_pattern = r"^##\s+Milestone\s+\d+"
        milestones = re.findall(milestone_pattern, content, re.MULTILINE)

        assert len(milestones) >= 2, f"Expected at least 2 milestones, found {len(milestones)}"
        assert len(milestones) <= 4, f"Expected at most 4 milestones, found {len(milestones)}"


class TestTechStackTemplate:
    """Test suite for tech-stack template organization."""

    def test_has_category_based_organization(self):
        """Test: Tech-stack template has category-based organization.

        Template must include these categories:
        - Languages
        - Frameworks
        - Database
        - Infrastructure
        - Development Tools
        """
        content = read_template("tech-stack-template.md")

        required_categories = [
            "Languages",
            "Frameworks",
            "Database",
            "Infrastructure",
            "Development Tools",
        ]

        for category in required_categories:
            pattern = rf"^##\s+{category}"
            match = re.search(pattern, content, re.MULTILINE)
            assert match is not None, f"Missing required category: {category}"

    def test_uses_simple_list_format(self):
        """Test: Tech-stack template uses simple list format.

        Categories should use bullet point lists without complex table structures
        for the main technology listings.
        """
        content = read_template("tech-stack-template.md")

        bullet_pattern = r"^-\s+\*\*.+\*\*"
        bullets = re.findall(bullet_pattern, content, re.MULTILINE)

        assert len(bullets) >= 10, f"Expected at least 10 bulleted items, found {len(bullets)}"

    def test_includes_example_technologies(self):
        """Test: Tech-stack template includes example technologies for each category.

        Template should provide realistic technology examples users can reference.
        """
        content = read_template("tech-stack-template.md")

        example_techs = [
            "TypeScript",
            "Python",
            "React",
            "PostgreSQL",
            "Git",
        ]

        found_examples = sum(1 for tech in example_techs if tech in content)
        assert found_examples >= 3, (
            f"Expected at least 3 example technologies from {example_techs}, "
            f"found {found_examples}"
        )
