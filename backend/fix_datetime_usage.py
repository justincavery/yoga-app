#!/usr/bin/env python3
"""
Fix deprecated datetime.utcnow() usage throughout the codebase.
Replaces datetime.utcnow() with datetime.now(timezone.utc)
"""
import re
import os
from pathlib import Path


def fix_datetime_in_file(file_path: Path) -> tuple[bool, int]:
    """
    Fix deprecated datetime usage in a single file.

    Returns:
        tuple[bool, int]: (was_modified, num_replacements)
    """
    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content

    # Check if file uses datetime.utcnow()
    if 'datetime.utcnow()' not in content:
        return False, 0

    # Count replacements
    replacements = content.count('datetime.utcnow()')

    # Check if timezone is already imported
    has_timezone_import = False
    datetime_import_pattern = r'from datetime import ([^;\n]+)'
    match = re.search(datetime_import_pattern, content)

    if match:
        imports = match.group(1)
        if 'timezone' in imports:
            has_timezone_import = True
        else:
            # Add timezone to existing import
            new_imports = imports.strip() + ', timezone'
            content = content.replace(
                f'from datetime import {imports}',
                f'from datetime import {new_imports}'
            )
    else:
        # No datetime import found - add it at the top after docstring
        lines = content.split('\n')
        insert_index = 0

        # Skip shebang and docstring
        for i, line in enumerate(lines):
            if i == 0 and line.startswith('#!'):
                insert_index = i + 1
                continue
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                # Find end of docstring
                quote = '"""' if '"""' in line else "'''"
                if line.count(quote) >= 2:
                    insert_index = i + 1
                    break
                else:
                    for j in range(i + 1, len(lines)):
                        if quote in lines[j]:
                            insert_index = j + 1
                            break
                break

        lines.insert(insert_index, 'from datetime import datetime, timezone')
        content = '\n'.join(lines)

    # Replace datetime.utcnow() with datetime.now(timezone.utc)
    content = content.replace('datetime.utcnow()', 'datetime.now(timezone.utc)')

    # Write back if modified
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True, replacements

    return False, 0


def main():
    """Fix datetime usage in all Python files in app/ directory."""
    backend_dir = Path(__file__).parent
    app_dir = backend_dir / 'app'

    files_modified = 0
    total_replacements = 0

    print("Fixing deprecated datetime.utcnow() usage...")
    print("-" * 60)

    # Find all Python files
    for py_file in app_dir.rglob('*.py'):
        # Skip backup files
        if '.bak' in py_file.name or '__pycache__' in str(py_file):
            continue

        modified, count = fix_datetime_in_file(py_file)
        if modified:
            files_modified += 1
            total_replacements += count
            print(f"✅ {py_file.relative_to(backend_dir)}: {count} replacements")

    print("-" * 60)
    print(f"✅ Complete!")
    print(f"   Files modified: {files_modified}")
    print(f"   Total replacements: {total_replacements}")


if __name__ == "__main__":
    main()
