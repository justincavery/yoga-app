#!/usr/bin/env python3
"""
Revert timezone-aware datetime usage back to naive UTC.
Replaces datetime.now(timezone.utc) with datetime.utcnow() for DB operations.
"""
import re
from pathlib import Path


def revert_datetime_in_file(file_path: Path) -> tuple[bool, int]:
    """
    Revert datetime usage in a single file.

    Returns:
        tuple[bool, int]: (was_modified, num_replacements)
    """
    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content

    # Count replacements
    replacements = content.count('datetime.now(timezone.utc)')

    if replacements == 0:
        return False, 0

    # Replace datetime.now(timezone.utc) with datetime.utcnow()
    content = content.replace('datetime.now(timezone.utc)', 'datetime.utcnow()')

    # Remove timezone import if it's now unused
    if 'timezone' not in content:
        # Remove from import statement
        content = re.sub(r'from datetime import ([^;\n]*), timezone([^;\n]*)', r'from datetime import \1\2', content)
        content = re.sub(r'from datetime import timezone, ([^;\n]*)', r'from datetime import \1', content)
        content = re.sub(r'from datetime import timezone\n', '', content)

    # Write back if modified
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True, replacements

    return False, 0


def main():
    """Revert datetime usage in all Python files in app/ directory."""
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / 'app'

    files_modified = 0
    total_replacements = 0

    print("Reverting timezone-aware datetime usage to naive UTC...")
    print("-" * 60)

    # Find all Python files in app/
    for py_file in app_dir.rglob('*.py'):
        # Skip test files and backup files
        if '__pycache__' in str(py_file) or '.bak' in py_file.name:
            continue

        modified, count = revert_datetime_in_file(py_file)
        if modified:
            files_modified += 1
            total_replacements += count
            print(f"✅ {py_file.relative_to(backend_dir)}: {count} replacements")

    print("-" * 60)
    print(f"✅ Complete!")
    print(f"   Files modified: {files_modified}")
    print(f"   Total replacements: {total_replacements}")
    print("\nNOTE: This reverts to datetime.utcnow() which is deprecated in Python 3.12+")
    print("but works correctly with TIMESTAMP WITHOUT TIME ZONE columns.")


if __name__ == "__main__":
    main()
