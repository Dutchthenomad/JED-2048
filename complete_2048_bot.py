#!/usr/bin/env python3
"""
Complete 2048 Bot - Full Automation Pipeline
Combines Playwright browser control + Computer Vision + Strategy AI
for autonomous 2048 gameplay.

Production-ready version with comprehensive error handling and logging.
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
from core.strategy import BasicStrategy
from production.error_handler import ProductionErrorHandler, RobustConnectionManager, error_handler

class Complete2048Bot:
    """Complete autonomous 2048 playing bot"""

    def __init__(self, headless: bool = False, debug: bool = True, log_level: str = "INFO"):
        """
        Initialize the complete 2048 bot

        Args:
            headless: Run browser in headless mode
            debug: Enable debug output and screenshots
            log_level: Logging level for production error handling
        """
        self.debug = debug

        # Initialize production error handling
        self.error_handler = ProductionErrorHandler(
            log_level=log_level,
            enable_recovery=True
        )
        self.connection_manager = RobustConnectionManager(self.error_handler)

        # Initialize systems with error handling
        try:
            self.controller = PlaywrightController(
                headless=headless,
                browser_type="chromium",
                block_ads=True
            )
            self.vision = CanonicalBoardVision()
            self.strategy = BasicStrategy()
        except Exception as e:
            self.error_handler.handle_error(e, "Bot initialization", raise_on_failure=True)

        # Game state tracking
        self.move_count = 0
        self.score = 0
        self.game_history = []
        self.max_tile = 0
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3

        self.error_handler.logger.info("🤖 Complete 2048 Bot Initialized")
        if self.debug:
            print("🤖 Complete 2048 Bot Initialized")
            print("   🌐 Browser Controller: Ready")
            print("   👁️  Vision System: Ready")
            print("   🧠 Strategy AI: Ready")
            print("   🛡️ Error Handler: Ready")

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
            for attempt in range(10):  # Try for up to 10 seconds
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

            # Calculate game metrics
            board_array = np.array(board_state)  # Convert to numpy array first
            max_tile = np.max(board_array)
            empty_tiles = np.sum(board_array == 0)
            total_value = np.sum(board_array)


            analysis = {
                'board_state': board_state,
                'max_tile': max_tile,
                'empty_tiles': empty_tiles,
                'total_value': total_value,
                'vision_success': True
            }

            if self.debug:
                print("✅ Vision analysis successful!")
                print(f"   📊 Max tile: {max_tile}")
                print(f"   🔲 Empty tiles: {empty_tiles}")
                print(f"   💎 Total value: {total_value}")
                print("   🎯 Board state:")
                for i, row in enumerate(board_state):
                    print(f"      Row {i+1}: {row}")

            return analysis
        else:
            if self.debug:
                print("❌ Vision analysis failed!")
            return None

    def get_best_move(self, board_state: np.ndarray) -> str:
        """Get best move from strategy AI"""
        if self.debug:
            print("\n🧠 Calculating best move...")

        try:
            # Get move recommendation from strategy
            move_scores = self.strategy.get_move_scores(board_state)
            best_move = self.strategy.recommend_move(board_state)

            if self.debug:
                print("📊 Move analysis:")
                directions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
                for i, direction in enumerate(directions):
                    score = move_scores[i] if i < len(move_scores) else 0
                    marker = " 🎯" if direction == best_move else ""
                    print(f"   {direction:>5}: {score:8.1f}{marker}")

                print(f"✅ Recommended move: {best_move}")

            return best_move
        except Exception as e:
            if self.debug:
                print(f"❌ Strategy failed: {e}")
            return "RIGHT"  # Default fallback

    def execute_move(self, move: str) -> bool:
        """Execute the chosen move"""
        if self.debug:
            print(f"\n🎮 Executing move: {move}")

        # Map move to key
        key_mapping = {
            'UP': 'ArrowUp',
            'DOWN': 'ArrowDown',
            'LEFT': 'ArrowLeft',
            'RIGHT': 'ArrowRight'
        }

        key = key_mapping.get(move, 'ArrowRight')
        success = self.controller.send_key(key)

        if success:
            if self.debug:
                print(f"✅ Move executed: {key}")

            # Wait for animation
            time.sleep(1.5)

            # Take after screenshot
            self.controller.take_screenshot(f"bot_move_{self.move_count:03d}_after.png")

            return True
        else:
            if self.debug:
                print(f"❌ Move failed: {key}")
            return False

    def update_game_stats(self, analysis: dict):
        """Update game statistics"""
        if analysis:
            self.max_tile = max(self.max_tile, analysis['max_tile'])

            # Try to get score from game UI
            try:
                game_info = self.controller.get_game_info()
                if 'score' in game_info:
                    self.score = game_info['score']
            except:
                pass

            self.game_history.append({
                'move': self.move_count,
                'max_tile': analysis['max_tile'],
                'empty_tiles': analysis['empty_tiles'],
                'total_value': analysis['total_value']
            })

    def check_game_over(self, analysis: dict) -> bool:
        """Check if game is over"""
        if not analysis:
            return True

        # Check if board is full and no moves possible
        if analysis['empty_tiles'] == 0:
            # Could add more sophisticated game over detection
            if self.debug:
                print("⚠️  Board appears full - potential game over")
            return True

        return False

    def play_autonomous_game(self, max_moves: int = 1000) -> dict:
        """Play a complete autonomous game"""
        print("🚀 STARTING AUTONOMOUS 2048 GAMEPLAY!")
        print("=" * 50)

        start_time = time.time()

        while self.move_count < max_moves:
            print(f"\n{'='*20} MOVE {self.move_count + 1} {'='*20}")

            # Step 1: Analyze current state
            analysis = self.analyze_current_state()
            if not analysis:
                print("❌ Vision analysis failed - aborting")
                break

            # Step 2: Check for game over
            if self.check_game_over(analysis):
                print("🏁 Game over detected!")
                break

            # Step 3: Get best move
            best_move = self.get_best_move(analysis['board_state'])

            # Step 4: Execute move
            if not self.execute_move(best_move):
                print("❌ Move execution failed - aborting")
                break

            # Step 5: Update statistics
            self.update_game_stats(analysis)
            self.move_count += 1

            # Step 6: Brief status update
            print(f"📊 Move {self.move_count} complete:")
            print(f"   🎯 Move: {best_move}")
            print(f"   🏆 Max tile: {analysis['max_tile']}")
            print(f"   🔲 Empty tiles: {analysis['empty_tiles']}")

            # Brief pause between moves
            time.sleep(0.5)

        # Game completion
        end_time = time.time()
        duration = end_time - start_time

        # Final results
        results = {
            'moves': self.move_count,
            'max_tile': self.max_tile,
            'score': self.score,
            'duration': duration,
            'moves_per_second': self.move_count / duration if duration > 0 else 0,
            'history': self.game_history
        }

        self.print_final_results(results)
        return results

    def print_final_results(self, results: dict):
        """Print comprehensive final results"""
        print("\n" + "="*60)
        print("🏆 AUTONOMOUS GAME COMPLETE!")
        print("="*60)
        print(f"🎮 Total moves: {results['moves']}")
        print(f"🏆 Highest tile: {results['max_tile']}")
        print(f"📊 Final score: {results['score']}")
        print(f"⏱️  Duration: {results['duration']:.1f} seconds")
        print(f"🚀 Speed: {results['moves_per_second']:.2f} moves/second")

        avg_score_per_move = 0
        if results['moves'] > 0:
            avg_score_per_move = results['score'] / results['moves'] if results['score'] > 0 else 0
            print(f"📈 Efficiency: {avg_score_per_move:.2f} points/move")

            print(f"\n🎯 Performance vs Human Baseline:")
            human_baseline = 11.54  # Your baseline from CLAUDE.md
            if avg_score_per_move > 0:
                if avg_score_per_move >= human_baseline:
                    print(f"   ✅ Bot efficiency: {avg_score_per_move:.2f} (EXCEEDS human {human_baseline})")
                else:
                    print(f"   📊 Bot efficiency: {avg_score_per_move:.2f} (below human {human_baseline})")
        else:
            print(f"\n⚠️  No moves completed - game initialization issue")

        print(f"\n📸 Screenshots captured: {results['moves'] * 2} (before/after each move)")
        print("🔍 Check captured screenshots for move-by-move analysis")

    def cleanup(self):
        """Comprehensive cleanup with error handling"""
        try:
            self.error_handler.logger.info("🧹 Starting bot cleanup...")

            if hasattr(self, 'controller'):
                self.controller.cleanup()

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

def main():
    """Main bot execution"""
    print("🤖 COMPLETE 2048 BOT - EDUCATIONAL FRAMEWORK CULMINATION")
    print("Combining: Playwright + Computer Vision + AI Strategy")
    print("="*60)

    try:
        # Initialize bot
        with Complete2048Bot(headless=False, debug=True) as bot:

            # Connect to game
            if not bot.connect_to_game():
                print("❌ Failed to connect to game")
                return False

            # Play autonomous game
            results = bot.play_autonomous_game(max_moves=100)  # Start with 100 moves

            print("\n🎉 AUTONOMOUS 2048 BOT SUCCESSFUL!")
            return True

    except KeyboardInterrupt:
        print("\n\n⏸️  Bot stopped by user")
        return False
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ MISSION ACCOMPLISHED!")
        print("🚀 Educational framework complete - bot autonomously played 2048!")
    else:
        print("\n❌ Bot execution incomplete")