#!/usr/bin/env python3
"""
Integration Tests for 2048 Bot System
Tests the complete pipeline: Screenshot → Vision → Strategy → Move Decision

Uses real screenshot data for comprehensive end-to-end validation.
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.improved_vision import ImprovedBoardVision
from core.strategy import BasicStrategy, Move
import cv2

class TestIntegration(unittest.TestCase):
    """End-to-end integration tests"""

    def setUp(self):
        self.vision = ImprovedBoardVision()
        self.strategy = BasicStrategy(debug_mode=False)

    def test_complete_pipeline_mature_game(self):
        """Test complete pipeline on mature game state"""
        # Load real screenshot
        image_path = project_root / "validation_data" / "easy_captures" / "2048_capture_20250917_222936_01.png"
        image = cv2.imread(str(image_path))
        self.assertIsNotNone(image, "Screenshot should load successfully")

        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Vision: Extract board state
        vision_results = self.vision.analyze_board(image)
        self.assertTrue(vision_results['success'], "Vision analysis should succeed")

        board_state = vision_results['board_state']
        expected_board = [[2,8,4,2], [2,8,64,32], [32,128,8,4], [4,32,16,2]]
        self.assertEqual(board_state, expected_board, "Should extract correct board state")

        # Strategy: Get move recommendation
        move, analysis = self.strategy.get_best_move(board_state)
        self.assertIsInstance(move, Move, "Should return valid move")
        self.assertIn('best_score', analysis, "Should include analysis data")

        # Validate move makes sense for this board state
        self.assertIn(move, [Move.UP, Move.DOWN], "Should choose UP or DOWN for full board")

    def test_complete_pipeline_early_game(self):
        """Test complete pipeline on early game state"""
        # Load early game screenshot
        image_path = project_root / "validation_data" / "easy_captures" / "2048_capture_20250917_212313_01.png"
        image = cv2.imread(str(image_path))
        self.assertIsNotNone(image)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Vision analysis
        vision_results = self.vision.analyze_board(image)
        self.assertTrue(vision_results['success'])

        board_state = vision_results['board_state']

        # Strategy analysis
        move, analysis = self.strategy.get_best_move(board_state)
        self.assertIsInstance(move, Move)

        # For early game, all moves should be possible
        possible_moves = [m for m, data in analysis['move_analysis'].items()
                         if data.get('possible', True)]
        self.assertGreater(len(possible_moves), 0, "Should have at least one possible move")

    def test_game_over_detection(self):
        """Test pipeline handles game over state correctly"""
        # Load game over screenshot
        image_path = project_root / "validation_data" / "easy_captures" / "2048_capture_20250917_223121_01.png"
        image = cv2.imread(str(image_path))
        self.assertIsNotNone(image)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Vision analysis
        vision_results = self.vision.analyze_board(image)
        self.assertTrue(vision_results['success'])

        board_state = vision_results['board_state']

        # Strategy analysis
        move, analysis = self.strategy.get_best_move(board_state)

        # Game over: no moves should be possible
        possible_moves = [m for m, data in analysis['move_analysis'].items()
                         if data.get('possible', True)]
        self.assertEqual(len(possible_moves), 0, "Game over state should have no possible moves")

    def test_strategy_consistency(self):
        """Test that strategy gives consistent results for same board state"""
        # Use a known board state
        board_state = [[2,8,4,2], [2,8,64,32], [32,128,8,4], [4,32,16,2]]

        # Run strategy multiple times
        results = []
        for _ in range(5):
            move, analysis = self.strategy.get_best_move(board_state)
            results.append(move)

        # All results should be the same
        self.assertTrue(all(move == results[0] for move in results),
                       "Strategy should be deterministic")

    def test_move_simulation_accuracy(self):
        """Test that move simulation produces valid results"""
        board_state = [[2,0,2,0], [0,4,0,0], [0,0,8,0], [0,0,0,16]]

        for move in Move:
            result = self.strategy._simulate_move(board_state, move)

            if result is not None:
                # Result should be valid 4x4 board
                self.assertEqual(len(result), 4, "Result should have 4 rows")
                for row in result:
                    self.assertEqual(len(row), 4, "Each row should have 4 tiles")
                    for tile in row:
                        self.assertGreaterEqual(tile, 0, "Tiles should be non-negative")

class TestSystemReliability(unittest.TestCase):
    """Test system reliability and error handling"""

    def setUp(self):
        self.vision = ImprovedBoardVision()
        self.strategy = BasicStrategy(debug_mode=False)

    def test_invalid_board_handling(self):
        """Test strategy handles invalid boards gracefully"""
        invalid_boards = [
            [],  # Empty board
            [[1, 2, 3]],  # Wrong size
            [[1, 2, 3, 4], [1, 2, 3, 4]],  # Incomplete
            [[1, 2, 3, -1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],  # Negative values
        ]

        for invalid_board in invalid_boards:
            move, analysis = self.strategy.get_best_move(invalid_board)
            self.assertIn('error', analysis, "Should include error information")

    def test_strategy_robustness(self):
        """Test strategy with edge case board states"""
        edge_cases = [
            [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],  # Empty board
            [[2, 4, 8, 16], [2, 4, 8, 16], [2, 4, 8, 16], [2, 4, 8, 16]],  # Full board
            [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],  # Single tile
        ]

        for board in edge_cases:
            move, analysis = self.strategy.get_best_move(board)
            self.assertIsInstance(move, Move, "Should return valid move even for edge cases")

def run_integration_tests():
    """Run all integration tests"""
    print("🔧 Running Integration Tests")
    print("=" * 40)
    print("Testing complete pipeline with real data\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemReliability))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print(f"\n📊 Integration Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print(f"   ✅ All integration tests passed!")
        return True
    else:
        print(f"   ❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)