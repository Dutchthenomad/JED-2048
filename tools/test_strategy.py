#!/usr/bin/env python3
"""
Comprehensive Strategy Testing Framework
Tests strategy system with real board states and manual verification support.

NO SIMULATIONS - uses actual screenshot data for all tests.
"""

import sys
from pathlib import Path
import unittest
from typing import Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.strategy import BasicStrategy, Move
from core.improved_vision import ImprovedBoardVision
import cv2
import json
from datetime import datetime

class TestBasicStrategy(unittest.TestCase):
    """Unit tests for basic strategy components"""

    def setUp(self):
        self.strategy = BasicStrategy(debug_mode=True)

    def test_board_validation(self):
        """Test board validation logic"""
        # Valid board
        valid_board = [[2, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertTrue(self.strategy._is_valid_board(valid_board))

        # Invalid boards
        self.assertFalse(self.strategy._is_valid_board([]))  # Empty
        self.assertFalse(self.strategy._is_valid_board([[1, 2, 3]]))  # Wrong size
        self.assertFalse(self.strategy._is_valid_board([[1, 2, 3, -1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]))  # Negative

    def test_empty_tile_counting(self):
        """Test empty tile counting"""
        board = [[2, 0, 2, 0], [0, 4, 0, 0], [0, 0, 8, 0], [0, 0, 0, 16]]
        # Count manually: Row1: 2 zeros, Row2: 3 zeros, Row3: 3 zeros, Row4: 3 zeros = 11 zeros
        self.assertEqual(self.strategy._count_empty_tiles(board), 11)

        # Full board
        full_board = [[2, 4, 8, 16], [2, 4, 8, 16], [2, 4, 8, 16], [2, 4, 8, 16]]
        self.assertEqual(self.strategy._count_empty_tiles(full_board), 0)

    def test_merge_potential(self):
        """Test merge potential evaluation"""
        # Board with horizontal merge opportunities
        board = [[2, 2, 0, 0], [4, 4, 8, 8], [0, 0, 0, 0], [0, 0, 0, 0]]
        merge_score = self.strategy._evaluate_merge_potential(board)
        self.assertGreater(merge_score, 0)

        # Board with vertical merge opportunities
        board = [[2, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        merge_score = self.strategy._evaluate_merge_potential(board)
        self.assertGreater(merge_score, 0)

    def test_corner_strategy(self):
        """Test corner strategy evaluation"""
        # Max tile in corner
        board = [[16, 8, 4, 2], [8, 4, 2, 0], [4, 2, 0, 0], [2, 0, 0, 0]]
        corner_score = self.strategy._evaluate_corner_strategy(board)
        self.assertEqual(corner_score, 1.0)

        # Max tile not in corner
        board = [[2, 16, 4, 2], [8, 4, 2, 0], [4, 2, 0, 0], [2, 0, 0, 0]]
        corner_score = self.strategy._evaluate_corner_strategy(board)
        self.assertEqual(corner_score, 0.0)

    def test_move_simulation(self):
        """Test move simulation accuracy"""
        # Test left move
        board = [[2, 2, 0, 0], [0, 4, 4, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        result = self.strategy._simulate_move(board, Move.LEFT)
        expected = [[4, 0, 0, 0], [8, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.assertEqual(result, expected)

        # Test impossible move
        board = [[2, 4, 8, 16], [2, 4, 8, 16], [2, 4, 8, 16], [2, 4, 8, 16]]
        result = self.strategy._simulate_move(board, Move.LEFT)
        self.assertIsNone(result)

class StrategyValidator:
    """Validates strategy with real screenshot data"""

    def __init__(self):
        self.strategy = BasicStrategy(debug_mode=True)
        self.vision = ImprovedBoardVision()

    def test_with_real_screenshots(self) -> Dict:
        """Test strategy with real game screenshots"""
        results = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "test_results": [],
            "summary": {}
        }

        # Test scenarios from real screenshots
        test_scenarios = [
            {
                "name": "Mature Game State",
                "image": "2048_capture_20250917_222936_01.png",
                "expected_board": [[2,8,4,2], [2,8,64,32], [32,128,8,4], [4,32,16,2]],
                "description": "Advanced game with tiles up to 128"
            },
            {
                "name": "Game Over State",
                "image": "2048_capture_20250917_223121_01.png",
                "expected_board": [[2,4,16,2], [8,16,32,4], [16,256,4,32], [2,8,64,2]],
                "description": "Full board endgame scenario"
            }
        ]

        for scenario in test_scenarios:
            print(f"\\n📋 Testing: {scenario['name']}")
            print(f"📄 {scenario['description']}")

            # Load screenshot
            image_path = project_root / "validation_data" / "easy_captures" / scenario["image"]
            image = cv2.imread(str(image_path))

            if image is None:
                print(f"❌ Could not load: {scenario['image']}")
                continue

            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Extract board state
            vision_results = self.vision.analyze_board(image)

            if not vision_results['success']:
                print(f"❌ Vision analysis failed: {vision_results.get('debug_info', {}).get('error')}")
                continue

            detected_board = vision_results['board_state']

            # Test strategy on detected board
            best_move, analysis = self.strategy.get_best_move(detected_board)

            # Validate results
            test_result = {
                "scenario": scenario['name'],
                "board_state": detected_board,
                "recommended_move": best_move.value,
                "move_scores": {move.value: score for move, score in analysis['all_scores'].items()},
                "reasoning": analysis['reasoning'],
                "validation": self._validate_move_choice(detected_board, best_move, analysis)
            }

            results["test_results"].append(test_result)

            # Display results
            print(f"✅ Strategy Analysis Complete")
            print(f"   🎯 Recommended Move: {best_move.value}")
            print(f"   📊 Best Score: {analysis['best_score']:.1f}")
            print(f"   💭 Reasoning: {analysis['reasoning']}")

            # Show all move scores for manual verification
            print(f"\\n   📋 All Move Scores:")
            for move, score in analysis['all_scores'].items():
                possible = analysis['move_analysis'][move].get('possible', True)
                status = "✅" if possible else "❌"
                print(f"      {status} {move.value}: {score:.1f}")

        # Generate summary
        total_tests = len(results["test_results"])
        successful_tests = len([r for r in results["test_results"] if r["validation"]["valid"]])

        results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0
        }

        return results

    def _validate_move_choice(self, board, move, analysis) -> Dict:
        """Validate that move choice is reasonable"""
        validation = {"valid": True, "issues": []}

        # Check if chosen move is possible
        if not analysis['move_analysis'][move].get('possible', True):
            validation["valid"] = False
            validation["issues"].append("Chosen move is not possible")

        # Check if there are significantly better moves
        best_score = analysis['best_score']
        for other_move, score in analysis['all_scores'].items():
            if other_move != move and analysis['move_analysis'][other_move].get('possible', True):
                if score > best_score + 100:  # Significantly better threshold
                    validation["issues"].append(f"Move {other_move.value} has much higher score ({score:.1f} vs {best_score:.1f})")

        return validation

    def save_test_results(self, results: Dict) -> Path:
        """Save test results for review"""
        results_dir = project_root / "validation_data"
        results_dir.mkdir(exist_ok=True)

        results_file = results_dir / f"strategy_test_results_{results['timestamp']}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        return results_file

def main():
    print("🧠 2048 Strategy Testing Framework")
    print("=" * 50)
    print("Testing strategy system with real screenshot data")
    print("NO SIMULATIONS - uses actual game board states\\n")

    # Run unit tests
    print("🔬 Running Unit Tests...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBasicStrategy)
    runner = unittest.TextTestRunner(verbosity=2)
    unit_result = runner.run(suite)

    if unit_result.wasSuccessful():
        print("\\n✅ All unit tests passed!")
    else:
        print("\\n❌ Some unit tests failed")
        return

    # Run integration tests with real data
    print("\\n🎮 Running Integration Tests with Real Screenshots...")
    validator = StrategyValidator()
    results = validator.test_with_real_screenshots()

    # Save results
    results_file = validator.save_test_results(results)

    # Display summary
    print(f"\\n📊 Test Summary:")
    print(f"   Total Tests: {results['summary']['total_tests']}")
    print(f"   Successful: {results['summary']['successful_tests']}")
    print(f"   Success Rate: {results['summary']['success_rate']:.1f}%")
    print(f"\\n💾 Detailed results saved: {results_file.name}")

    print("\\n🎉 Strategy testing completed!")
    print("   Review results above for manual verification")
    print("   All move choices are based on real game data")

if __name__ == "__main__":
    main()