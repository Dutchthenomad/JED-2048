#!/usr/bin/env python3
"""
GUI-Enhanced 2048 Bot
Extended version of Enhanced2048Bot with debug GUI integration
"""

import sys
from pathlib import Path
import time
import cv2
import numpy as np
import logging
import argparse
from typing import Optional, Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from enhanced_2048_bot import Enhanced2048Bot
from gui import DebugInterface, GUIConfig
from gui.bot_controls import BotState
from core.screenshot_manager import screenshot_manager

class GUIEnhanced2048Bot(Enhanced2048Bot):
    """
    Enhanced 2048 bot with debug GUI integration

    Extends the existing bot with real-time visual debugging capabilities
    """

    def __init__(self, headless: bool = False, debug: bool = True, log_level: str = "INFO",
                 algorithm_id: str = None, gui_enabled: bool = False):
        """
        Initialize GUI-enhanced bot

        Args:
            headless: Run browser in headless mode (ignored if GUI enabled)
            debug: Enable debug output
            log_level: Logging level
            algorithm_id: Algorithm to use
            gui_enabled: Enable debug GUI interface
        """
        # Force non-headless when GUI is enabled
        if gui_enabled:
            headless = False

        super().__init__(headless=headless, debug=debug, log_level=log_level,
                        algorithm_id=algorithm_id)

        # GUI components
        self.gui_enabled = gui_enabled
        self.debug_gui: Optional[DebugInterface] = None
        self.gui_config = GUIConfig()

        # GUI integration state
        self.gui_bot_state = BotState.STOPPED
        self.last_cv_data = None
        self.performance_start_time = time.time()

        # Initialize screenshot session
        if algorithm_id:
            screenshot_manager.start_session(algorithm_id)
        else:
            screenshot_manager.start_session("Enhanced Heuristic")

        if self.gui_enabled:
            self._initialize_gui()

    def _initialize_gui(self):
        """Initialize the debug GUI"""
        try:
            self.debug_gui = DebugInterface(self.gui_config)
            self.debug_gui.register_bot(self)

            # Register bot control callbacks
            self.debug_gui.control_panel.register_callback("start", self._gui_start_bot)
            self.debug_gui.control_panel.register_callback("stop", self._gui_stop_bot)
            self.debug_gui.control_panel.register_callback("pause", self._gui_pause_bot)
            self.debug_gui.control_panel.register_callback("emergency_stop", self._gui_emergency_stop)

            # Start GUI
            self.debug_gui.start()
            time.sleep(0.5)  # Let GUI initialize

            self.error_handler.logger.info("🖥️ Debug GUI initialized successfully")
            if self.debug:
                print("🖥️ Debug GUI initialized successfully")

        except Exception as e:
            self.error_handler.logger.error(f"Failed to initialize GUI: {e}")
            self.gui_enabled = False

    def take_screenshot_with_gui_update(self, filename: str = None) -> Optional[np.ndarray]:
        """Enhanced screenshot capture with GUI integration"""
        # Take screenshot using parent method
        screenshot_bgr = self.controller.take_screenshot(filename)
        if screenshot_bgr is None:
            return None

        screenshot_rgb = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2RGB)

        # Save to organized screenshot system
        if filename:
            # Extract move number and type from filename
            import re
            match = re.search(r'bot_move_(\d+)_(\w+)', filename)
            if match:
                move_num = int(match.group(1))
                screenshot_type = match.group(2)
                organized_path = screenshot_manager.save_screenshot_file(filename, move_num, screenshot_type)

                # CRITICAL FIX: Direct memory-to-GUI update (avoid file I/O bottleneck)
                if self.gui_enabled and self.debug_gui:
                    self.debug_gui.update_screenshot(screenshot_rgb)
            else:
                # Fallback to direct GUI update
                if self.gui_enabled and self.debug_gui:
                    self.debug_gui.update_screenshot(screenshot_rgb)
        else:
            # Direct GUI update for screenshots without filenames
            if self.gui_enabled and self.debug_gui:
                self.debug_gui.update_screenshot(screenshot_rgb)

        return screenshot_rgb

    def analyze_board_with_gui_update(self, screenshot: np.ndarray) -> Dict[str, Any]:
        """Enhanced board analysis with GUI visualization"""
        # Perform normal vision analysis
        result = self.vision.analyze_board(screenshot)

        # Create CV visualization data for GUI
        if self.gui_enabled and self.debug_gui and result.get('success'):
            overlay_payload = {
                'board_region': result.get('board_region'),
                'tile_positions': result.get('tile_positions'),
                'tile_mapping': result.get('tile_mapping'),
                'confidence_map': result.get('confidence_map'),
                'processing_time': result.get('processing_time')
            }

            self.last_cv_data = overlay_payload

            self.debug_gui.update_cv_analysis(overlay_payload)
            self.debug_gui.update_board_state(result['board_state'])

        return result

    def make_move_with_gui_update(self, move: str) -> bool:
        """Enhanced move execution with GUI updates"""
        # Update GUI state
        if self.gui_enabled and self.debug_gui:
            metrics = self._calculate_current_metrics()
            self.debug_gui.update_metrics(metrics)

        # Execute move using parent method
        success = self.controller.send_key(f"Arrow{move.capitalize()}")

        return success

    def play_autonomous_game(self, max_moves: int = 1000) -> Dict[str, Any]:
        """Enhanced autonomous gameplay with GUI integration"""
        if self.gui_enabled and self.debug_gui:
            self._update_gui_bot_state(BotState.RUNNING)

        try:
            # Override parent method to integrate GUI updates
            start_time = time.time()
            moves_completed = 0
            game_data = []

            while moves_completed < max_moves:
                # Check for GUI stop commands
                if self.gui_enabled and self.gui_bot_state == BotState.STOPPED:
                    break

                # Take screenshot with GUI update
                screenshot = self.take_screenshot_with_gui_update(
                    f"bot_move_{self.move_count:03d}_before.png"
                )

                if screenshot is None:
                    break

                # Analyze with GUI update
                result = self.analyze_board_with_gui_update(screenshot)

                if not result['success']:
                    break

                board_state = result['board_state']

                # Get move from algorithm
                move = self.current_algorithm.get_move(board_state)

                # Execute move with GUI update
                if self.make_move_with_gui_update(move):
                    self.move_count += 1
                    moves_completed += 1

                    # Brief pause for GUI updates
                    time.sleep(0.1)
                else:
                    break

            # Calculate final results
            duration = time.time() - start_time
            return {
                'moves_completed': moves_completed,
                'duration_seconds': duration,
                'final_score': self.score,
                'highest_tile': self.max_tile
            }

        except Exception as e:
            self.error_handler.logger.error(f"Game error: {e}")
            return {'error': str(e)}

        finally:
            if self.gui_enabled and self.debug_gui:
                self._update_gui_bot_state(BotState.STOPPED)

    def _calculate_current_metrics(self) -> Dict[str, Any]:
        """Calculate current performance metrics for GUI"""
        current_time = time.time()
        elapsed = current_time - self.performance_start_time

        efficiency = self.score / max(self.move_count, 1)
        vision_time = 0.0
        if self.last_cv_data and isinstance(self.last_cv_data, dict):
            vision_time = float(self.last_cv_data.get('processing_time') or 0.0) * 1000.0
        moves_per_second = self.move_count / max(elapsed, 1)

        return {
            'current_score': self.score,
            'move_count': self.move_count,
            'efficiency': efficiency,
            'highest_tile': self.max_tile,
            'elapsed_time': elapsed,
            'moves_per_second': moves_per_second,
            'moves_per_sec': moves_per_second,
            'vision_time': vision_time,
            'gui_fps': 30  # TODO: Calculate actual GUI FPS
        }

    def _update_gui_bot_state(self, state: BotState):
        """Update GUI bot state"""
        self.gui_bot_state = state
        if self.debug_gui and hasattr(self.debug_gui, 'control_panel'):
            self.debug_gui.control_panel.update_bot_state(state)

    def _gui_start_bot(self):
        """GUI callback: Start bot"""
        if self.gui_bot_state == BotState.STOPPED:
            self._update_gui_bot_state(BotState.RUNNING)
            # TODO: Implement start logic

    def _gui_stop_bot(self):
        """GUI callback: Stop bot"""
        self._update_gui_bot_state(BotState.STOPPED)

    def _gui_pause_bot(self):
        """GUI callback: Pause bot"""
        if self.gui_bot_state == BotState.RUNNING:
            self._update_gui_bot_state(BotState.PAUSED)
        elif self.gui_bot_state == BotState.PAUSED:
            self._update_gui_bot_state(BotState.RUNNING)

    def _gui_emergency_stop(self):
        """GUI callback: Emergency stop"""
        self._update_gui_bot_state(BotState.STOPPED)
        # TODO: Implement emergency stop logic

    def cleanup(self):
        """Enhanced cleanup with GUI shutdown"""
        try:
            if self.gui_enabled and self.debug_gui:
                self.debug_gui.stop()
                time.sleep(0.5)  # Allow GUI to shutdown

            # Cleanup screenshot session
            screenshot_manager.cleanup_session(keep_latest=5)
            screenshot_manager.end_session()

            # Call parent cleanup
            super().cleanup()

        except Exception as e:
            self.error_handler.logger.error(f"Cleanup error: {e}")

def main():
    """Main entry point with GUI support"""
    parser = argparse.ArgumentParser(description="JED-2048 Bot with Debug GUI")
    parser.add_argument("--gui", action="store_true",
                       help="Enable debug GUI interface")
    parser.add_argument("--headless", action="store_true",
                       help="Run browser in headless mode (ignored with --gui)")
    parser.add_argument("--algorithm", type=str,
                       help="Algorithm to use")
    parser.add_argument("--max-moves", type=int, default=500,
                       help="Maximum moves per game")

    args = parser.parse_args()

    print("🤖 JED-2048 GUI-Enhanced Bot")
    print("=" * 40)

    if args.gui:
        print("🖥️ Debug GUI mode enabled")
    else:
        print("🎮 Standard bot mode")

    try:
        # Initialize bot
        bot = GUIEnhanced2048Bot(
            headless=args.headless,
            debug=True,
            algorithm_id=args.algorithm,
            gui_enabled=args.gui
        )

        # Connect to game
        if not bot.connect_to_game():
            print("❌ Failed to connect to game")
            return

        # Run game
        results = bot.play_autonomous_game(max_moves=args.max_moves)

        # Display results
        if 'error' not in results:
            print(f"\n📊 Game completed:")
            print(f"   Moves: {results['moves_completed']}")
            print(f"   Duration: {results['duration_seconds']:.1f}s")
            print(f"   Score: {results.get('final_score', 0)}")
            print(f"   Highest tile: {results.get('highest_tile', 0)}")

    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        if 'bot' in locals():
            bot.cleanup()

if __name__ == "__main__":
    main()
