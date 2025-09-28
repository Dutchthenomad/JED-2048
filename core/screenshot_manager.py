#!/usr/bin/env python3
"""
Screenshot Management System for 2048 Bot GUI
Handles organized screenshot storage, retrieval, and GUI integration
"""

import os
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import json
import shutil


class ScreenshotSession:
    """Manages a single bot session's screenshots"""

    def __init__(self, algorithm_name: str, session_id: Optional[str] = None):
        self.algorithm_name = algorithm_name
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self.start_time = datetime.now()
        self.screenshot_count = 0
        self.screenshots = []

        # Create session directory
        self.base_dir = Path("temp/sessions") / f"{self.session_id}_{algorithm_name.replace(' ', '_')}"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Save session metadata
        self.metadata_file = self.base_dir / "session_info.json"
        self._save_metadata()

    def _save_metadata(self):
        """Save session metadata to file"""
        metadata = {
            'session_id': self.session_id,
            'algorithm_name': self.algorithm_name,
            'start_time': self.start_time.isoformat(),
            'screenshot_count': self.screenshot_count,
            'screenshots': self.screenshots
        }

        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def add_screenshot(self, move_number: int, screenshot_type: str, source_path: str) -> str:
        """Add a screenshot to this session"""
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"move_{move_number:03d}_{screenshot_type}_{timestamp}.png"
        dest_path = self.base_dir / filename

        # Copy screenshot to session directory
        if os.path.exists(source_path):
            shutil.copy2(source_path, dest_path)

            # Add to tracking
            screenshot_info = {
                'move_number': move_number,
                'type': screenshot_type,
                'filename': filename,
                'path': str(dest_path),
                'timestamp': timestamp
            }

            self.screenshots.append(screenshot_info)
            self.screenshot_count += 1
            self._save_metadata()

            return str(dest_path)

        return ""

    def get_latest_screenshot(self) -> Optional[str]:
        """Get path to most recent screenshot"""
        if self.screenshots:
            return self.screenshots[-1]['path']
        return None

    def get_screenshots_by_move(self, move_number: int) -> List[Dict[str, Any]]:
        """Get all screenshots for a specific move"""
        return [s for s in self.screenshots if s['move_number'] == move_number]

    def cleanup(self):
        """Clean up session files"""
        if self.base_dir.exists():
            shutil.rmtree(self.base_dir)


class ScreenshotManager:
    """Central screenshot management for GUI integration"""

    def __init__(self):
        self.current_session: Optional[ScreenshotSession] = None
        self.temp_dir = Path("temp/screenshots")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Clean up any existing temp files
        self._cleanup_temp_files()

    def start_session(self, algorithm_name: str) -> str:
        """Start a new screenshot session"""
        if self.current_session:
            self.end_session()

        self.current_session = ScreenshotSession(algorithm_name)
        return self.current_session.session_id

    def end_session(self):
        """End current session"""
        if self.current_session:
            self.current_session = None

    def save_screenshot(self, screenshot_data: bytes, move_number: int, screenshot_type: str = "before") -> str:
        """Save screenshot data and return path for GUI display"""
        if not self.current_session:
            # Create temporary session if none exists
            self.start_session("Unknown")

        # Save to temp file first
        timestamp = int(time.time() * 1000)  # milliseconds for uniqueness
        temp_filename = f"temp_{move_number:03d}_{screenshot_type}_{timestamp}.png"
        temp_path = self.temp_dir / temp_filename

        # Write screenshot data
        with open(temp_path, 'wb') as f:
            f.write(screenshot_data)

        # Add to session
        session_path = self.current_session.add_screenshot(move_number, screenshot_type, str(temp_path))

        return session_path if session_path else str(temp_path)

    def save_screenshot_file(self, source_path: str, move_number: int, screenshot_type: str = "before") -> str:
        """Save existing screenshot file and return organized path"""
        if not self.current_session:
            self.start_session("Unknown")

        if os.path.exists(source_path):
            session_path = self.current_session.add_screenshot(move_number, screenshot_type, source_path)
            return session_path if session_path else source_path

        return ""

    def get_latest_screenshot_path(self) -> Optional[str]:
        """Get path to latest screenshot for GUI display"""
        if self.current_session:
            return self.current_session.get_latest_screenshot()
        return None

    def get_session_screenshots(self) -> List[Dict[str, Any]]:
        """Get all screenshots from current session"""
        if self.current_session:
            return self.current_session.screenshots
        return []

    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        if self.temp_dir.exists():
            for file in self.temp_dir.glob("temp_*.png"):
                try:
                    file.unlink()
                except OSError:
                    pass

    def cleanup_session(self, keep_latest: int = 10):
        """Clean up current session, optionally keeping latest screenshots"""
        if self.current_session and keep_latest > 0:
            # Keep only latest screenshots
            screenshots = self.current_session.screenshots[-keep_latest:]

            # Remove old screenshot files
            for screenshot in self.current_session.screenshots[:-keep_latest]:
                try:
                    Path(screenshot['path']).unlink()
                except OSError:
                    pass

            # Update session data
            self.current_session.screenshots = screenshots
            self.current_session.screenshot_count = len(screenshots)
            self.current_session._save_metadata()


class AlgorithmComparisonManager:
    """Manages screenshots for algorithm comparison studies"""

    def __init__(self):
        self.comparison_dir = Path("temp/algorithm_comparisons")
        self.comparison_dir.mkdir(parents=True, exist_ok=True)
        self.active_comparison: Optional[str] = None
        self.algorithm_sessions: Dict[str, ScreenshotSession] = {}

    def start_comparison(self, comparison_name: str) -> str:
        """Start a new algorithm comparison"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_id = f"{comparison_name}_{timestamp}"

        self.active_comparison = comparison_id
        self.algorithm_sessions = {}

        # Create comparison directory
        comparison_path = self.comparison_dir / comparison_id
        comparison_path.mkdir(parents=True, exist_ok=True)

        return comparison_id

    def add_algorithm_session(self, algorithm_name: str, session: ScreenshotSession):
        """Add an algorithm session to the comparison"""
        if self.active_comparison:
            self.algorithm_sessions[algorithm_name] = session

            # Copy session to comparison directory
            comparison_path = self.comparison_dir / self.active_comparison
            algorithm_dir = comparison_path / algorithm_name.replace(' ', '_')

            if session.base_dir.exists():
                shutil.copytree(session.base_dir, algorithm_dir, dirs_exist_ok=True)

    def get_comparison_data(self) -> Dict[str, Any]:
        """Get data for current comparison"""
        if not self.active_comparison:
            return {}

        comparison_data = {
            'comparison_id': self.active_comparison,
            'algorithms': {},
            'summary': {}
        }

        for algo_name, session in self.algorithm_sessions.items():
            comparison_data['algorithms'][algo_name] = {
                'session_id': session.session_id,
                'screenshot_count': session.screenshot_count,
                'screenshots': session.screenshots
            }

        return comparison_data

    def save_comparison_report(self) -> str:
        """Save comparison report to file"""
        if not self.active_comparison:
            return ""

        comparison_data = self.get_comparison_data()
        report_path = self.comparison_dir / self.active_comparison / "comparison_report.json"

        with open(report_path, 'w') as f:
            json.dump(comparison_data, f, indent=2)

        return str(report_path)


# Global managers for easy access
screenshot_manager = ScreenshotManager()
comparison_manager = AlgorithmComparisonManager()