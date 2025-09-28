#!/usr/bin/env python3
"""
Cleanup Agent for 2048 Educational Platform
Automatically identifies and manages development artifacts and unused files.
"""

import os
import re
import json
import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set, Optional
import argparse
import subprocess

@dataclass
class CleanupCandidate:
    """Represents a file or directory that could be cleaned up."""
    path: str
    reason: str
    category: str
    size_bytes: int
    last_modified: datetime.datetime
    risk_level: str  # low, medium, high

class CleanupAgent:
    """Intelligent cleanup agent for the 2048 educational platform."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.candidates: List[CleanupCandidate] = []
        self.protected_patterns = self._load_protected_patterns()
        self.cleanup_rules = self._load_cleanup_rules()

    def _load_protected_patterns(self) -> Set[str]:
        """Define patterns for files that should never be cleaned up."""
        return {
            # Core algorithm files
            'algorithms/*/algorithm.py',
            'algorithms/base_algorithm.py',
            'algorithms/algorithm_manager.py',

            # Core system files
            'core/*.py',
            'run_visible_bot.py',
            'enhanced_2048_bot.py',

            # Configuration and docs
            'README.md',
            'INSTALLATION.md',
            'CONTRIBUTING.md',
            'requirements*.txt',
            '.gitignore',
            'LICENSE',
            'Makefile',

            # Production files
            'production/**/*',

            # Essential directories
            '.git/**/*',
            '.venv/**/*',
            '__pycache__/**/*',
        }

    def _load_cleanup_rules(self) -> Dict[str, Dict]:
        """Define cleanup rules with categories and risk levels."""
        return {
            'test_files': {
                'patterns': [r'test_.*\.py$', r'.*_test\.py$'],
                'exceptions': ['tests/'],  # Keep organized test directory
                'risk_level': 'low',
                'description': 'Temporary test scripts outside organized test directory'
            },
            'debug_files': {
                'patterns': [r'debug_.*\.py$', r'.*_debug\.py$'],
                'risk_level': 'low',
                'description': 'Debug scripts and temporary debugging files'
            },
            'screenshot_artifacts': {
                'patterns': [r'.*\.(png|jpg|jpeg)$'],
                'exceptions': ['docs/', 'assets/'],  # Keep documentation images
                'risk_level': 'low',
                'description': 'Screenshot files from testing and debugging'
            },
            'temporary_docs': {
                'patterns': [r'.*_(PLAN|COMPLETE|IMPLEMENTATION)\.md$'],
                'risk_level': 'medium',
                'description': 'Temporary implementation and planning documents'
            },
            'duplicate_bots': {
                'patterns': [r'.*_2048_bot\.py$', r'complete_2048_bot\.py$'],
                'exceptions': ['enhanced_2048_bot.py', 'run_visible_bot.py'],
                'risk_level': 'medium',
                'description': 'Duplicate or outdated bot implementations'
            },
            'temp_files': {
                'patterns': [r'temp_.*', r'.*\.tmp$', r'.*\.temp$'],
                'risk_level': 'low',
                'description': 'Temporary files and caches'
            },
            'orphaned_configs': {
                'patterns': [r'.*\.json$', r'.*\.yaml$', r'.*\.yml$'],
                'exceptions': ['package.json', 'config/'],
                'risk_level': 'high',
                'description': 'Configuration files that may be orphaned'
            }
        }

    def _is_protected(self, file_path: Path) -> bool:
        """Check if a file matches any protected pattern."""
        relative_path = file_path.relative_to(self.project_root)

        for pattern in self.protected_patterns:
            if relative_path.match(pattern):
                return True
        return False

    def _categorize_file(self, file_path: Path) -> Optional[CleanupCandidate]:
        """Categorize a file based on cleanup rules."""
        if self._is_protected(file_path):
            return None

        relative_path = file_path.relative_to(self.project_root)
        filename = file_path.name

        for category, rules in self.cleanup_rules.items():
            # Check if file matches any pattern
            for pattern in rules['patterns']:
                if re.match(pattern, filename) or re.match(pattern, str(relative_path)):
                    # Check exceptions
                    if 'exceptions' in rules:
                        skip = False
                        for exception in rules['exceptions']:
                            if exception in str(relative_path):
                                skip = True
                                break
                        if skip:
                            continue

                    # Create cleanup candidate
                    stat = file_path.stat()
                    return CleanupCandidate(
                        path=str(file_path),
                        reason=rules['description'],
                        category=category,
                        size_bytes=stat.st_size,
                        last_modified=datetime.datetime.fromtimestamp(stat.st_mtime),
                        risk_level=rules['risk_level']
                    )

        return None

    def scan_project(self) -> List[CleanupCandidate]:
        """Scan the project for cleanup candidates."""
        self.candidates = []

        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                candidate = self._categorize_file(file_path)
                if candidate:
                    self.candidates.append(candidate)

        # Sort by risk level and size
        risk_order = {'low': 0, 'medium': 1, 'high': 2}
        self.candidates.sort(key=lambda x: (risk_order[x.risk_level], -x.size_bytes))

        return self.candidates

    def generate_report(self) -> str:
        """Generate a detailed cleanup report."""
        if not self.candidates:
            return "No cleanup candidates found. Project is clean!"

        report = []
        report.append("# 2048 Educational Platform - Cleanup Report")
        report.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total candidates: {len(self.candidates)}")

        # Summary by category
        by_category = {}
        total_size = 0

        for candidate in self.candidates:
            if candidate.category not in by_category:
                by_category[candidate.category] = {'count': 0, 'size': 0}
            by_category[candidate.category]['count'] += 1
            by_category[candidate.category]['size'] += candidate.size_bytes
            total_size += candidate.size_bytes

        report.append(f"\nTotal reclaimable space: {self._format_size(total_size)}")
        report.append("\n## Summary by Category")

        for category, stats in by_category.items():
            report.append(f"- {category}: {stats['count']} files, {self._format_size(stats['size'])}")

        # Detailed listing by risk level
        for risk_level in ['low', 'medium', 'high']:
            risk_candidates = [c for c in self.candidates if c.risk_level == risk_level]
            if risk_candidates:
                report.append(f"\n## {risk_level.upper()} Risk Items ({len(risk_candidates)} files)")

                for candidate in risk_candidates:
                    relative_path = Path(candidate.path).relative_to(self.project_root)
                    report.append(f"- `{relative_path}` ({self._format_size(candidate.size_bytes)})")
                    report.append(f"  - {candidate.reason}")
                    report.append(f"  - Modified: {candidate.last_modified.strftime('%Y-%m-%d %H:%M')}")

        return "\n".join(report)

    def _format_size(self, bytes_size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f}TB"

    def execute_cleanup(self, risk_levels: List[str] = None, dry_run: bool = True) -> Dict:
        """Execute cleanup for specified risk levels."""
        if risk_levels is None:
            risk_levels = ['low']

        results = {
            'removed': [],
            'errors': [],
            'total_size_freed': 0
        }

        candidates_to_clean = [
            c for c in self.candidates
            if c.risk_level in risk_levels
        ]

        for candidate in candidates_to_clean:
            try:
                if dry_run:
                    print(f"[DRY RUN] Would remove: {candidate.path}")
                    results['removed'].append(candidate.path)
                    results['total_size_freed'] += candidate.size_bytes
                else:
                    os.remove(candidate.path)
                    print(f"Removed: {candidate.path}")
                    results['removed'].append(candidate.path)
                    results['total_size_freed'] += candidate.size_bytes

            except Exception as e:
                error_msg = f"Failed to remove {candidate.path}: {str(e)}"
                print(f"ERROR: {error_msg}")
                results['errors'].append(error_msg)

        return results

# TODO(human) - Implement specialized cleanup rules
def create_specialized_rules():
    """
    Add domain-specific cleanup rules for the 2048 educational platform.

    Consider:
    - Algorithm versioning patterns (old_algorithm_v1.py, etc.)
    - Student submission cleanup (keeping only latest versions)
    - Log file rotation and cleanup
    - Model checkpoint cleanup for ML algorithms

    Return a dictionary of additional cleanup rules to merge with the base rules.
    """
    pass

def main():
    """Main entry point for the cleanup agent."""
    parser = argparse.ArgumentParser(description='2048 Educational Platform Cleanup Agent')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--scan-only', action='store_true', help='Only scan and report, no cleanup')
    parser.add_argument('--risk-levels', nargs='+', choices=['low', 'medium', 'high'],
                       default=['low'], help='Risk levels to clean')
    parser.add_argument('--dry-run', action='store_true', default=True, help='Show what would be removed')
    parser.add_argument('--execute', action='store_true', help='Actually perform cleanup (overrides dry-run)')
    parser.add_argument('--report-file', help='Save report to file')

    args = parser.parse_args()

    # Initialize cleanup agent
    agent = CleanupAgent(args.project_root)

    # Scan for candidates
    print("Scanning project for cleanup candidates...")
    candidates = agent.scan_project()

    # Generate report
    report = agent.generate_report()
    print("\n" + report)

    if args.report_file:
        with open(args.report_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {args.report_file}")

    # Execute cleanup if requested
    if not args.scan_only and candidates:
        dry_run = not args.execute
        results = agent.execute_cleanup(args.risk_levels, dry_run=dry_run)

        print(f"\nCleanup Summary:")
        print(f"Files processed: {len(results['removed'])}")
        print(f"Space freed: {agent._format_size(results['total_size_freed'])}")
        if results['errors']:
            print(f"Errors: {len(results['errors'])}")

if __name__ == "__main__":
    main()