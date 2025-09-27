#!/usr/bin/env python3
"""
Update Path References for Fork
Updates all hardcoded paths in JSON files and documentation for the new project location.
"""

import json
import os
from pathlib import Path

def update_json_paths():
    """Update paths in JSON training data files"""
    print("🔧 Updating JSON training data paths...")

    # Define path mapping
    old_path = "/home/nomad/Desktop/SOLANA EDU/PythonGamingScratchPad/2048-demo"
    new_path = "/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo"

    # Find all JSON files in validation_data
    project_root = Path(__file__).parent.parent
    validation_dir = project_root / "validation_data"

    json_files = list(validation_dir.glob("*.json"))

    updated_count = 0
    for json_file in json_files:
        print(f"   📄 Processing: {json_file.name}")

        try:
            # Read JSON file
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Convert to string for replacement
            json_str = json.dumps(data, indent=2)

            # Replace old paths with new paths
            if old_path in json_str:
                json_str = json_str.replace(old_path, new_path)

                # Parse back to JSON
                updated_data = json.loads(json_str)

                # Write back to file
                with open(json_file, 'w') as f:
                    json.dump(updated_data, f, indent=2)

                print(f"      ✅ Updated paths in {json_file.name}")
                updated_count += 1
            else:
                print(f"      ℹ️  No paths to update in {json_file.name}")

        except Exception as e:
            print(f"      ❌ Error updating {json_file.name}: {e}")

    print(f"   📊 Updated {updated_count} JSON files")

def clean_cache_files():
    """Remove Python cache files with old paths"""
    print("\n🧹 Cleaning Python cache files...")

    project_root = Path(__file__).parent.parent

    # Find and remove __pycache__ directories
    cache_dirs = list(project_root.rglob("__pycache__"))

    removed_count = 0
    for cache_dir in cache_dirs:
        try:
            # Remove all .pyc files in the directory
            for pyc_file in cache_dir.glob("*.pyc"):
                pyc_file.unlink()
                removed_count += 1

            # Remove the directory if empty
            if not any(cache_dir.iterdir()):
                cache_dir.rmdir()
                print(f"   🗑️  Removed cache directory: {cache_dir}")
        except Exception as e:
            print(f"   ❌ Error cleaning {cache_dir}: {e}")

    print(f"   📊 Removed {removed_count} cache files")

def verify_paths():
    """Verify that path updates were successful"""
    print("\n🔍 Verifying path updates...")

    old_path = "/home/nomad/Desktop/SOLANA EDU/PythonGamingScratchPad/2048-demo"
    project_root = Path(__file__).parent.parent

    # Check for any remaining old paths in text files
    remaining_issues = []

    for file_path in project_root.rglob("*.py"):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if old_path in content:
                    remaining_issues.append(f"Python file: {file_path}")
        except:
            continue

    for file_path in project_root.rglob("*.json"):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if old_path in content:
                    remaining_issues.append(f"JSON file: {file_path}")
        except:
            continue

    for file_path in project_root.rglob("*.md"):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if old_path in content:
                    remaining_issues.append(f"Markdown file: {file_path}")
        except:
            continue

    if remaining_issues:
        print("   ⚠️  Found remaining old paths:")
        for issue in remaining_issues:
            print(f"      - {issue}")
    else:
        print("   ✅ All paths successfully updated!")

    return len(remaining_issues) == 0

def main():
    """Update all path references for the fork"""
    print("🔄 Path Update Tool for 2048 Playwright Fork")
    print("=" * 50)
    print("Updating hardcoded paths for new project location\n")

    # Step 1: Update JSON files
    update_json_paths()

    # Step 2: Clean cache files
    clean_cache_files()

    # Step 3: Verify updates
    success = verify_paths()

    # Summary
    print(f"\n📊 Path Update Summary")
    print("=" * 30)
    if success:
        print("✅ All paths successfully updated!")
        print("✅ Project ready for new location")
        print("\n🎯 Next steps:")
        print("1. Test basic functionality: python tools/quick_verification.py")
        print("2. Run integration tests: python tests/test_integration.py")
        print("3. Begin Playwright analysis: Phase P1")
    else:
        print("⚠️  Some paths may need manual attention")
        print("Please review the remaining issues above")

if __name__ == "__main__":
    main()