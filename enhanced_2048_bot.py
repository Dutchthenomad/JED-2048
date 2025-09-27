#!/usr/bin/env python3
"""
Enhanced 2048 Bot with Algorithm Selection
Supports pluggable algorithms for educational platform
"""

import sys
from pathlib import Path
import time
import cv2
import numpy as np
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.playwright_controller import PlaywrightController
from core.canonical_vision import CanonicalBoardVision
from production.error_handler import ProductionErrorHandler, RobustConnectionManager, error_handler
from algorithms import AlgorithmManager, BaseAlgorithm

class Enhanced2048Bot:
    """
    Enhanced 2048 bot with pluggable algorithm support

    Allows runtime algorithm selection and switching for educational platform
    """

    def __init__(self, headless: bool = False, debug: bool = True, log_level: str = "INFO",
                 algorithm_id: str = None):
        """
        Initialize enhanced bot with algorithm selection

        Args:
            headless: Run browser in headless mode
            debug: Enable debug output and screenshots
            log_level: Logging level for error handling
            algorithm_id: Specific algorithm to use (if None, uses default)
        """
        self.debug = debug

        # Initialize production error handling
        self.error_handler = ProductionErrorHandler(
            log_level=log_level,
            enable_recovery=True
        )
        self.connection_manager = RobustConnectionManager(self.error_handler)

        # Initialize core systems
        try:
            self.controller = PlaywrightController(
                headless=headless,
                browser_type="chromium",
                block_ads=True
            )
            self.vision = CanonicalBoardVision()
        except Exception as e:
            self.error_handler.handle_error(e, "Bot initialization", raise_on_failure=True)

        # Initialize algorithm manager
        self.algorithm_manager = AlgorithmManager()
        self.current_algorithm = None
        self.algorithm_id = None

        # Set initial algorithm
        if algorithm_id:
            self.set_algorithm(algorithm_id)
        else:
            self._set_default_algorithm()

        # Game state tracking
        self.move_count = 0
        self.score = 0
        self.game_history = []
        self.max_tile = 0
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3

        self.error_handler.logger.info("🤖 Enhanced 2048 Bot Initialized")
        if self.debug:
            print("🤖 Enhanced 2048 Bot Initialized")
            print("   🌐 Browser Controller: Ready")
            print("   👁️  Vision System: Ready")
            print(f"   🧠 Algorithm: {self.current_algorithm.metadata.name if self.current_algorithm else 'None'}")
            print("   🛡️ Error Handler: Ready")
            print("   🔧 Algorithm Manager: Ready")

    def set_algorithm(self, algorithm_id: str, **config) -> bool:
        """
        Set the algorithm to use for gameplay

        Args:
            algorithm_id: Algorithm identifier
            **config: Algorithm configuration parameters

        Returns:
            True if algorithm set successfully
        """
        try:
            new_algorithm = self.algorithm_manager.get_algorithm(algorithm_id, **config)
            if new_algorithm:
                self.current_algorithm = new_algorithm
                self.algorithm_id = algorithm_id
                self.error_handler.logger.info(f"✅ Algorithm set to: {algorithm_id}")
                if self.debug:
                    print(f"🧠 Algorithm switched to: {new_algorithm.metadata.name} v{new_algorithm.metadata.version}")
                return True
            else:
                self.error_handler.logger.error(f"❌ Algorithm {algorithm_id} not found")
                return False
        except Exception as e:
            self.error_handler.handle_error(e, f"Setting algorithm {algorithm_id}")
            return False

    def list_available_algorithms(self):
        """List all available algorithms"""
        algorithms = self.algorithm_manager.list_algorithms()

        print("🧠 Available Algorithms:")
        print("=" * 50)

        for algo in algorithms:
            print(f"📊 {algo['name']} v{algo['version']}")
            print(f"   ID: {algo['id']}")
            print(f"   Type: {algo['type']}")
            print(f"   Author: {algo['author']}")
            print(f"   Description: {algo['description']}")
            if algo['performance_baseline']:
                print(f"   Baseline: {algo['performance_baseline']} points/move")
            print()

        return algorithms

    def get_algorithm_comparison(self, algorithm_ids: list = None):
        """Get performance comparison of algorithms"""
        if algorithm_ids is None:
            # Compare all algorithms with performance data
            algorithm_ids = list(self.algorithm_manager.performance_history.keys())

        if not algorithm_ids:
            print("📊 No performance data available for comparison")
            return {}

        comparison = self.algorithm_manager.compare_algorithms(algorithm_ids)

        print("📊 Algorithm Performance Comparison:")
        print("=" * 60)

        if 'rankings' in comparison:
            print("🏆 Efficiency Rankings:")
            for i, algo in enumerate(comparison['rankings']['by_efficiency'][:5], 1):
                print(f"   {i}. {algo['name']}: {algo['average_efficiency']:.2f} points/move")

            print("\n🎯 Highest Tile Rankings:")
            for i, algo in enumerate(comparison['rankings']['by_highest_tile'][:5], 1):
                print(f"   {i}. {algo['name']}: {algo['highest_tile']} tile")

        return comparison

    def _set_default_algorithm(self):
        """Set default algorithm (Enhanced Heuristic if available)"""
        algorithms = self.algorithm_manager.list_algorithms()

        # Try to find Enhanced Heuristic algorithm
        for algo in algorithms:
            if "Enhanced Heuristic" in algo['name']:
                self.set_algorithm(algo['id'])
                return

        # Fallback to first available algorithm
        if algorithms:
            self.set_algorithm(algorithms[0]['id'])
        else:
            self.error_handler.logger.warning("⚠️ No algorithms available")

    @error_handler("Game connection", max_retries=2)
    def connect_to_game(self, url: str = "https://2048game.com/") -> bool:
        """Connect to 2048 game with robust error handling"""
        self.error_handler.logger.info(f"🌐 Connecting to {url}...")

        # Use robust connection manager for fallback URLs
        if url == "https://2048game.com/":
            success = self.connection_manager.attempt_connection(self.controller)
        else:
            success = self.controller.connect(url)

        if success:
            self.error_handler.logger.info("✅ Connected successfully!")

            # Wait for game to fully load and initial tiles to appear
            for attempt in range(10):
                time.sleep(1)
                try:
                    screenshot = self.controller.take_screenshot("init_check.png")
                    if screenshot is not None:
                        result = self.vision.analyze_board(screenshot)
                        if result['success'] and np.sum(result['board_state']) > 0:
                            self.error_handler.logger.info(f"✅ Game initialized! Found tiles after {attempt + 1} seconds")
                            return True
                except Exception as e:
                    self.error_handler.handle_error(e, f"Game initialization check (attempt {attempt + 1})")

            self.error_handler.logger.warning("⚠️ Game may not have initialized properly, proceeding anyway...")
            return True
        else:
            self.error_handler.logger.error("❌ All connection attempts failed!")
            return False

    @error_handler("Board analysis", max_retries=2)
    def analyze_current_state(self) -> dict:
        """Analyze current game state using computer vision"""
        if self.debug:
            print("\n👁️  Analyzing game state...")

        # Take screenshot
        screenshot = self.controller.take_screenshot(f"bot_move_{self.move_count:03d}_before.png")
        if screenshot is None:
            if self.debug:
                print("❌ Screenshot failed!")
            return None

        # Analyze with vision system
        result = self.vision.analyze_board(screenshot)

        if result['success']:
            board_state = result['board_state']
            if self.debug:
                print(f"✅ Board analysis successful")
                self._print_board(board_state)

            return {
                'board_state': board_state,
                'empty_tiles': np.sum(np.array(board_state) == 0),
                'max_tile': np.max(board_state),
                'total_score': self._calculate_board_score(board_state)
            }
        else:
            if self.debug:
                print("❌ Board analysis failed!")
            return None

    def get_next_move(self, board_state) -> str:
        """Get next move using current algorithm"""
        if not self.current_algorithm:
            self.error_handler.logger.error("❌ No algorithm selected")
            return "UP"  # Fallback

        try:
            move = self.current_algorithm.get_move(board_state)
            if self.debug:
                print(f"🧠 Algorithm recommendation: {move}")

                # Get detailed scores if available
                try:
                    scores = self.current_algorithm.get_move_scores(board_state)
                    directions = ["UP", "DOWN", "LEFT", "RIGHT"]
                    print("   Move scores:")
                    for i, direction in enumerate(directions):
                        print(f"     {direction}: {scores[i]:.1f}")
                except Exception:
                    pass

            return move
        except Exception as e:
            self.error_handler.handle_error(e, "Algorithm move generation")
            return "UP"  # Fallback

    def play_autonomous_game(self, max_moves: int = 200) -> dict:
        """Play complete autonomous game with current algorithm"""
        game_start_time = time.time()
        self.move_count = 0
        initial_state = self.analyze_current_state()

        if not initial_state:
            return {'error': 'Failed to analyze initial game state'}

        if self.debug:
            print(f"\n🎮 Starting autonomous game with {self.current_algorithm.metadata.name}")
            print(f"⏱️  Maximum moves: {max_moves}")

        game_over = False
        moves_completed = 0

        while moves_completed < max_moves and not game_over:
            try:
                # Analyze current board
                current_state = self.analyze_current_state()
                if not current_state:
                    break

                board_state = current_state['board_state']

                # Get move from algorithm
                move = self.get_next_move(board_state)

                # Execute move
                success = self.controller.send_key(f"Arrow{move.lower().capitalize()}")
                if not success:
                    if self.debug:
                        print(f"❌ Failed to execute move: {move}")
                    break

                # Wait for animation
                time.sleep(0.5)

                # Take after screenshot and analyze
                self.controller.take_screenshot(f"bot_move_{self.move_count:03d}_after.png")
                self.move_count += 1
                moves_completed += 1

                # Check for game over
                try:
                    game_info = self.controller.get_game_info()
                    if game_info.get('game_over', False):
                        game_over = True
                        if self.debug:
                            print("🏁 Game over detected")
                except Exception:
                    pass

                if self.debug and moves_completed % 10 == 0:
                    print(f"📊 Progress: {moves_completed}/{max_moves} moves completed")

            except Exception as e:
                self.error_handler.handle_error(e, f"Game move {moves_completed + 1}")
                break

        # Calculate final results
        duration = time.time() - game_start_time
        final_state = self.analyze_current_state()

        results = {
            'algorithm_id': self.algorithm_id,
            'algorithm_name': self.current_algorithm.metadata.name if self.current_algorithm else 'Unknown',
            'moves_completed': moves_completed,
            'duration_seconds': duration,
            'final_score': final_state.get('total_score', 0) if final_state else 0,
            'highest_tile': final_state.get('max_tile', 0) if final_state else 0,
            'empty_tiles': final_state.get('empty_tiles', 0) if final_state else 0,
            'game_over': game_over,
            'efficiency': 0.0
        }

        # Calculate efficiency
        if moves_completed > 0:
            results['efficiency'] = results['final_score'] / moves_completed

        # Update algorithm statistics
        if self.current_algorithm:
            self.current_algorithm.update_stats(results)

            # Record performance in algorithm manager
            performance_data = self.current_algorithm.get_performance_metrics()
            self.algorithm_manager.record_performance(self.algorithm_id, performance_data)

        if self.debug:
            print(f"\n🎯 Game Complete!")
            print(f"   Algorithm: {results['algorithm_name']}")
            print(f"   Moves: {results['moves_completed']}")
            print(f"   Score: {results['final_score']}")
            print(f"   Highest tile: {results['highest_tile']}")
            print(f"   Efficiency: {results['efficiency']:.2f} points/move")
            print(f"   Duration: {results['duration_seconds']:.1f} seconds")

        return results

    def _print_board(self, board_state):
        """Print board state in readable format"""
        print("   Current board:")
        for row in board_state:
            print(f"     {[f'{tile:4d}' if tile > 0 else '   .' for tile in row]}")

    def _calculate_board_score(self, board_state):
        """Calculate approximate score from board state"""
        # Simple score estimation based on tile values
        score = 0
        for row in board_state:
            for tile in row:
                if tile >= 4:
                    # Score contribution is roughly (tile_value - 4) + previous merges
                    contribution = tile - 4
                    if tile >= 8:
                        contribution += (tile // 4) * 2
                    score += contribution
        return score

    def cleanup(self):
        """Comprehensive cleanup with error handling"""
        try:
            self.error_handler.logger.info("🧹 Starting bot cleanup...")

            if hasattr(self, 'controller'):
                self.controller.cleanup()

            # Save algorithm performance data
            if hasattr(self, 'algorithm_manager'):
                timestamp = int(time.time())
                performance_file = f"reports/algorithm_performance_{timestamp}.json"
                self.algorithm_manager.save_performance_data(performance_file)

            # Clean up temporary files (but keep logs)
            temp_files = Path(".").glob("bot_move_*.png")
            cleaned_count = 0
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                    cleaned_count += 1
                except Exception as e:
                    self.error_handler.logger.warning(f"Could not remove {temp_file}: {e}")

            if cleaned_count > 0:
                self.error_handler.logger.info(f"🗑️ Cleaned up {cleaned_count} temporary screenshot files")

            self.error_handler.logger.info("✅ Bot cleanup completed successfully")

        except Exception as e:
            if hasattr(self, 'error_handler'):
                self.error_handler.handle_error(e, "Bot cleanup")
            if self.debug:
                print(f"⚠️ Cleanup warning: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

if __name__ == "__main__":
    # Demo the enhanced bot with algorithm selection
    print("🤖 ENHANCED 2048 BOT - ALGORITHM SELECTION DEMO")
    print("=" * 60)

    try:
        # Initialize bot
        bot = Enhanced2048Bot(headless=False, debug=True)

        # Show available algorithms
        algorithms = bot.list_available_algorithms()

        if algorithms:
            # Try to set a specific algorithm
            print("🧠 Testing algorithm selection...")
            first_algo = algorithms[0]
            bot.set_algorithm(first_algo['id'])

            # Connect and play a short game
            if bot.connect_to_game():
                results = bot.play_autonomous_game(max_moves=20)
                print(f"\n🎉 Demo completed with {results['algorithm_name']}!")

        bot.cleanup()

    except KeyboardInterrupt:
        print("\n⏸️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()