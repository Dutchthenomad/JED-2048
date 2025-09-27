#!/usr/bin/env python3
"""
Bot Integration Tests
Tests the complete bot system with mocked browser for safety.

Tests all components working together without requiring actual browser.
"""

import sys
import unittest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.game_bot import GameBot, GameSession
from core.browser_controller import BrowserType, GameAction
from core.strategy import Move

class TestGameSession(unittest.TestCase):
    """Test game session tracking"""

    def test_session_creation(self):
        """Test session initialization"""
        session = GameSession()
        self.assertEqual(session.moves, 0)
        self.assertEqual(session.final_score, 0)
        self.assertFalse(session.completed)

    def test_move_logging(self):
        """Test move logging functionality"""
        session = GameSession()

        board_before = [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        board_after = [[0, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

        session.add_move(Move.DOWN, board_before, board_after, 0)

        self.assertEqual(session.moves, 1)
        self.assertEqual(len(session.move_log), 1)
        self.assertEqual(session.move_log[0]['move'], 'DOWN')

    def test_game_completion(self):
        """Test game completion tracking"""
        session = GameSession()
        session.add_move(Move.UP, [[]], [[]], 100)
        session.finish_game(200)

        self.assertTrue(session.completed)
        self.assertEqual(session.final_score, 200)
        self.assertEqual(session.efficiency, 200.0)  # 200 score / 1 move

class TestGameBotIntegration(unittest.TestCase):
    """Test game bot with mocked dependencies"""

    def setUp(self):
        """Setup test fixtures"""
        # Create mocked bot to avoid actual browser
        with patch('core.game_bot.BrowserController') as mock_browser_class, \
             patch('core.game_bot.ImprovedBoardVision') as mock_vision_class, \
             patch('core.game_bot.BasicStrategy') as mock_strategy_class:

            # Setup mocks
            self.mock_browser = Mock()
            self.mock_vision = Mock()
            self.mock_strategy = Mock()

            mock_browser_class.return_value = self.mock_browser
            mock_vision_class.return_value = self.mock_vision
            mock_strategy_class.return_value = self.mock_strategy

            # Create bot
            self.bot = GameBot(browser_type=BrowserType.FIREFOX, headless=True, debug_mode=True)

    def test_bot_initialization(self):
        """Test bot initializes correctly"""
        self.assertIsNotNone(self.bot.browser)
        self.assertIsNotNone(self.bot.vision)
        self.assertIsNotNone(self.bot.strategy)
        self.assertFalse(self.bot.running)
        self.assertFalse(self.bot.paused)

    def test_bot_startup(self):
        """Test bot startup process"""
        # Mock successful startup
        self.mock_browser.start_browser.return_value = True
        self.mock_browser.navigate_to_game.return_value = True

        result = self.bot.start_bot("https://test-game.com")

        self.assertTrue(result)
        self.assertTrue(self.bot.running)
        self.mock_browser.start_browser.assert_called_once()
        self.mock_browser.navigate_to_game.assert_called_once_with("https://test-game.com")

    def test_bot_startup_failure(self):
        """Test bot handles startup failures"""
        # Mock browser startup failure
        self.mock_browser.start_browser.return_value = False

        result = self.bot.start_bot("https://test-game.com")

        self.assertFalse(result)
        self.assertFalse(self.bot.running)

    def test_move_conversion(self):
        """Test move to action conversion"""
        # Test all move conversions
        conversions = {
            Move.UP: GameAction.UP,
            Move.DOWN: GameAction.DOWN,
            Move.LEFT: GameAction.LEFT,
            Move.RIGHT: GameAction.RIGHT
        }

        for move, expected_action in conversions.items():
            result = self.bot._move_to_action(move)
            self.assertEqual(result, expected_action)

    def test_failure_handling(self):
        """Test failure handling and recovery"""
        # Test consecutive failure tracking
        self.assertEqual(self.bot.consecutive_failures, 0)

        self.bot._handle_failure("Test error 1")
        self.assertEqual(self.bot.consecutive_failures, 1)

        self.bot._handle_failure("Test error 2")
        self.assertEqual(self.bot.consecutive_failures, 2)

        # Should still be running with 2 failures
        self.bot.running = True  # Simulate running state
        self.assertTrue(self.bot.running)

        # Trigger failure threshold
        for i in range(3):  # Add 3 more failures to reach 5 total
            self.bot._handle_failure(f"Test error {i+3}")

        # Should stop after max failures
        self.assertFalse(self.bot.running)

    def test_statistics_empty(self):
        """Test statistics with no games"""
        stats = self.bot.get_statistics()
        self.assertIn("message", stats)
        self.assertEqual(stats["message"], "No completed games")

    def test_statistics_with_games(self):
        """Test statistics calculation"""
        # Add some mock sessions
        session1 = GameSession()
        session1.moves = 100
        session1.final_score = 1000
        session1.efficiency = 10.0
        session1.highest_tile = 64
        session1.completed = True

        session2 = GameSession()
        session2.moves = 200
        session2.final_score = 2000
        session2.efficiency = 10.0
        session2.highest_tile = 128
        session2.completed = True

        self.bot.sessions = [session1, session2]

        stats = self.bot.get_statistics()

        self.assertEqual(stats["total_games"], 2)
        self.assertEqual(stats["total_score"], 3000)
        self.assertEqual(stats["total_moves"], 300)
        self.assertEqual(stats["average_score"], 1500.0)
        self.assertEqual(stats["average_moves"], 150.0)
        self.assertEqual(stats["average_efficiency"], 10.0)
        self.assertEqual(stats["highest_tile_achieved"], 128)
        self.assertEqual(stats["best_score"], 2000)

class TestBotComponents(unittest.TestCase):
    """Test individual bot components"""

    def test_component_imports(self):
        """Test all components can be imported"""
        from core.browser_controller import BrowserController, BrowserType, GameAction
        from core.game_bot import GameBot, GameSession
        from core.strategy import BasicStrategy, Move
        from core.improved_vision import ImprovedBoardVision

        # All imports should work without error
        self.assertTrue(True)

    def test_browser_types(self):
        """Test browser type enumeration"""
        from core.browser_controller import BrowserType

        self.assertEqual(BrowserType.FIREFOX.value, "firefox")
        self.assertEqual(BrowserType.CHROME.value, "chrome")

    def test_game_actions(self):
        """Test game action enumeration values (Playwright key names)"""
        from core.browser_controller import GameAction

        self.assertEqual(GameAction.UP.value, 'ArrowUp')
        self.assertEqual(GameAction.DOWN.value, 'ArrowDown')
        self.assertEqual(GameAction.LEFT.value, 'ArrowLeft')
        self.assertEqual(GameAction.RIGHT.value, 'ArrowRight')

def run_integration_tests():
    """Run all bot integration tests"""
    print("🤖 Running Bot Integration Tests")
    print("=" * 40)
    print("Testing complete bot system with mocked dependencies\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGameSession))
    suite.addTests(loader.loadTestsFromTestCase(TestGameBotIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestBotComponents))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print(f"\n📊 Integration Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print(f"   ✅ All bot integration tests passed!")
        return True
    else:
        print(f"   ❌ Some tests failed")

        # Show failures
        if result.failures:
            print("\n❌ Failures:")
            for test, traceback in result.failures:
                print(f"   {test}: {traceback.split('AssertionError:')[-1].strip()}")

        if result.errors:
            print("\n💥 Errors:")
            for test, traceback in result.errors:
                print(f"   {test}: {traceback.split(':')[-1].strip()}")

        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
