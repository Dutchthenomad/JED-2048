"""
2048 Game Bot - Main Automation System
Integrates vision, strategy, and browser control for autonomous gameplay.

Complete pipeline: Screenshot → Vision → Strategy → Action → Repeat
"""

import time
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np

from .browser_controller import BrowserController, BrowserType, GameAction
from .improved_vision import ImprovedBoardVision
from .strategy import BasicStrategy, Move

class GameBotError(Exception):
    """Custom exception for game bot errors"""
    pass

class GameSession:
    """Tracks data for a single game session"""

    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = None
        self.moves = 0
        self.final_score = 0
        self.highest_tile = 0
        self.efficiency = 0.0
        self.board_states = []
        self.move_log = []
        self.completed = False

    def add_move(self, move: Move, board_before: List[List[int]], board_after: List[List[int]], score: int):
        """Record a move"""
        self.moves += 1
        self.move_log.append({
            'move_number': self.moves,
            'move': move.value,
            'board_before': board_before,
            'board_after': board_after,
            'score': score,
            'timestamp': datetime.now()
        })

        if board_after and all(len(row) > 0 for row in board_after):
            self.highest_tile = max(max(row) for row in board_after)

    def finish_game(self, final_score: int):
        """Mark game as finished"""
        self.end_time = datetime.now()
        self.final_score = final_score
        self.efficiency = final_score / self.moves if self.moves > 0 else 0
        self.completed = True

class GameBot:
    """
    Main 2048 game bot
    Coordinates vision, strategy, and browser control for autonomous play
    """

    def __init__(self,
                 browser_type: BrowserType = BrowserType.FIREFOX,
                 headless: bool = False,
                 debug_mode: bool = False):

        # Initialize components
        self.browser = BrowserController(browser_type, headless)
        self.vision = ImprovedBoardVision()
        self.strategy = BasicStrategy(debug_mode=debug_mode)

        # Configuration
        self.debug_mode = debug_mode
        self.max_moves_per_game = 1000  # Safety limit
        self.max_consecutive_failures = 5  # Error tolerance
        self.screenshot_save_debug = debug_mode

        # State tracking
        self.current_session: Optional[GameSession] = None
        self.sessions: List[GameSession] = []
        self.running = False
        self.paused = False

        # Error tracking
        self.consecutive_failures = 0
        self.total_vision_failures = 0
        self.total_action_failures = 0

        # Setup logging
        self.logger = logging.getLogger(__name__)
        if debug_mode:
            self.logger.setLevel(logging.DEBUG)

    def start_bot(self, game_url: str) -> bool:
        """
        Start the bot and navigate to game
        Returns True if successful
        """
        try:
            self.logger.info("Starting 2048 game bot")

            # Start browser
            if not self.browser.start_browser():
                raise GameBotError("Failed to start browser")

            # Navigate to game
            if not self.browser.navigate_to_game(game_url):
                raise GameBotError("Failed to navigate to game")

            self.running = True
            self.logger.info("Bot started successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            self.stop_bot()
            return False

    def play_game(self) -> Optional[GameSession]:
        """
        Play a complete game from start to finish
        Returns game session data
        """
        if not self.running:
            self.logger.error("Bot not started")
            return None

        self.logger.info("Starting new game")
        self.current_session = GameSession()

        try:
            # Ensure we start fresh
            self._start_new_game()

            # Main game loop
            while self.running and not self.paused:
                if not self._play_single_turn():
                    break

                # Check if game ended
                game_state = self.browser.check_game_state()
                if game_state.get('game_over', False):
                    self.logger.info("Game over detected")
                    break

                # Safety check
                if self.current_session.moves >= self.max_moves_per_game:
                    self.logger.warning("Maximum moves reached")
                    break

            # Finalize session
            if self.current_session:
                final_score = self._get_final_score()
                self.current_session.finish_game(final_score)
                self.sessions.append(self.current_session)

                self.logger.info(f"Game completed: {final_score} points in {self.current_session.moves} moves "
                               f"(efficiency: {self.current_session.efficiency:.2f})")

                return self.current_session

        except GameBotError as e:
            self.logger.error(f"Game error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error during game: {e}")

        return self.current_session

    def _start_new_game(self) -> bool:
        """Start a new game"""
        try:
            # Check if new game button is available
            game_state = self.browser.check_game_state()

            if game_state.get('new_game_available', False):
                self.browser.send_game_action(GameAction.NEW_GAME)
                time.sleep(1)  # Wait for game to reset

            return True

        except Exception as e:
            self.logger.error(f"Failed to start new game: {e}")
            return False

    def _play_single_turn(self) -> bool:
        """
        Play one turn: capture → analyze → decide → act
        Returns True if successful, False if game should end
        """
        try:
            # Reset failure tracking on success
            self.consecutive_failures = 0

            # Step 1: Capture screenshot
            screenshot_bytes = self.browser.take_screenshot()
            if not screenshot_bytes:
                self._handle_failure("Screenshot capture failed")
                return False

            # Convert screenshot to OpenCV format
            image_array = np.frombuffer(screenshot_bytes, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Step 2: Analyze board state
            vision_results = self.vision.analyze_board(image, save_debug=self.screenshot_save_debug)
            if not vision_results['success']:
                self.total_vision_failures += 1
                self._handle_failure(f"Vision analysis failed: {vision_results.get('debug_info', {}).get('error', 'Unknown')}")
                return False

            current_board = vision_results['board_state']

            # Step 3: Get strategy recommendation
            best_move, analysis = self.strategy.get_best_move(current_board)

            if not analysis['move_analysis'][best_move].get('possible', True):
                self.logger.info("No valid moves available - game may be over")
                return False

            # Step 4: Execute move
            game_action = self._move_to_action(best_move)
            if not self.browser.send_game_action(game_action):
                self.total_action_failures += 1
                self._handle_failure(f"Failed to execute action: {best_move.value}")
                return False

            # Step 5: Verify move was successful (optional quick check)
            time.sleep(0.5)  # Brief wait for animation

            # Log the move
            if self.current_session:
                # Get score if possible
                game_state = self.browser.check_game_state()
                score = game_state.get('score', 0)

                # We'll get the new board state on next iteration for efficiency
                self.current_session.add_move(best_move, current_board, None, score)

            if self.debug_mode:
                self.logger.debug(f"Move {self.current_session.moves if self.current_session else '?'}: "
                                f"{best_move.value} (score: {analysis['best_score']:.1f})")

            return True

        except Exception as e:
            self._handle_failure(f"Turn execution failed: {e}")
            return False

    def _move_to_action(self, move: Move) -> GameAction:
        """Convert strategy move to browser action"""
        mapping = {
            Move.UP: GameAction.UP,
            Move.DOWN: GameAction.DOWN,
            Move.LEFT: GameAction.LEFT,
            Move.RIGHT: GameAction.RIGHT
        }
        return mapping[move]

    def _handle_failure(self, error_msg: str):
        """Handle failure with appropriate recovery"""
        self.consecutive_failures += 1
        self.logger.warning(f"Failure {self.consecutive_failures}/{self.max_consecutive_failures}: {error_msg}")

        if self.consecutive_failures >= self.max_consecutive_failures:
            self.logger.error("Too many consecutive failures - stopping game")
            self.running = False

    def _get_final_score(self) -> int:
        """Get final score from game"""
        try:
            game_state = self.browser.check_game_state()
            return game_state.get('score', 0)
        except:
            return 0

    def pause_bot(self):
        """Pause bot execution"""
        self.paused = True
        self.logger.info("Bot paused")

    def resume_bot(self):
        """Resume bot execution"""
        self.paused = False
        self.logger.info("Bot resumed")

    def stop_bot(self):
        """Stop bot and cleanup"""
        self.running = False
        self.paused = False

        if self.browser:
            self.browser.close_browser()

        self.logger.info("Bot stopped")

    def get_statistics(self) -> Dict[str, Any]:
        """Get bot performance statistics"""
        if not self.sessions:
            return {"message": "No completed games"}

        total_games = len(self.sessions)
        total_score = sum(s.final_score for s in self.sessions)
        total_moves = sum(s.moves for s in self.sessions)

        stats = {
            "total_games": total_games,
            "total_score": total_score,
            "total_moves": total_moves,
            "average_score": total_score / total_games,
            "average_moves": total_moves / total_games,
            "average_efficiency": total_score / total_moves if total_moves > 0 else 0,
            "highest_tile_achieved": max(s.highest_tile for s in self.sessions),
            "best_score": max(s.final_score for s in self.sessions),
            "best_efficiency": max(s.efficiency for s in self.sessions),
            "vision_failures": self.total_vision_failures,
            "action_failures": self.total_action_failures
        }

        return stats

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_bot()