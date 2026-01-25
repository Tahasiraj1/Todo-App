#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version

Usage:
    python quick_validate.py <skill_directory>

Example:
    python quick_validate.py .claude/skills/my-skill
"""

import sys
import re
from pathlib import Path


def validate_skill(skill_path: str | Path) -> tuple[bool, str]:
    """
    Basic validation of a skill.

    Args:
        skill_path: Path to the skill directory

    Returns:
        Tuple of (is_valid, message)
    """
    skill_path = Path(skill_path)

    # Check skill directory exists
    if not skill_path.exists():
        return False, f"Skill directory not found: {skill_path}"

    if not skill_path.is_dir():
        return False, f"Path is not a directory: {skill_path}"

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate content
    content = skill_md.read_text()

    # Check frontmatter exists
    if not content.startswith('---'):
        return False, "No YAML frontmatter found (must start with ---)"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format (missing closing ---)"

    frontmatter = match.group(1)

    # Check required fields
    if 'name:' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description:' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract and validate name
    name_match = re.search(r'name:\s*(.+)', frontmatter)
    if name_match:
        name = name_match.group(1).strip()

        # Check naming convention (hyphen-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"

        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"

        if len(name) > 64:
            return False, f"Name '{name}' exceeds 64 character limit"

        # Check name matches directory
        if name != skill_path.name:
            return False, f"Name '{name}' does not match directory name '{skill_path.name}'"

    # Extract and validate description
    desc_match = re.search(r'description:\s*\|?\s*\n?(.*?)(?=\n[a-z-]+:|$)', frontmatter, re.DOTALL)
    if desc_match:
        description = desc_match.group(1).strip()

        # Check for angle brackets (invalid in description)
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"

        # Check description length
        if len(description) > 1024:
            return False, f"Description exceeds 1024 character limit ({len(description)} chars)"

    # Check for TODO placeholders (warning, not failure)
    if '[TODO' in content:
        return True, "Skill is valid (but contains TODO placeholders)"

    # Check SKILL.md line count
    line_count = len(content.splitlines())
    if line_count > 500:
        return False, f"SKILL.md exceeds 500 lines ({line_count} lines) - move content to references/"

    return True, "Skill is valid!"


def main():
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        print("\nExample:")
        print("  python quick_validate.py .claude/skills/my-skill")
        sys.exit(1)

    skill_path = sys.argv[1]
    print(f"Validating skill: {skill_path}")
    print()

    valid, message = validate_skill(skill_path)

    if valid:
        print(f"PASS: {message}")
    else:
        print(f"FAIL: {message}")

    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
