#!/usr/bin/env python3
"""
Test script to compare enhanced heuristic strategy vs simple priorities
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.strategy import BasicStrategy

def test_enhanced_strategy():
    """Test enhanced heuristic strategy with various board scenarios"""
    print("🧠 ENHANCED STRATEGY VALIDATION TEST")
    print("=" * 60)
    print("🎯 Testing advanced heuristic evaluation vs simple priorities")
    print("")

    strategy = BasicStrategy()

    # Test scenarios that should show sophisticated decision making
    test_cases = [
        {
            "name": "Corner Strategy Test - Max tile should stay in corner",
            "board": [
                [16, 8, 4, 2],
                [8, 4, 2, 0],
                [4, 2, 0, 0],
                [2, 0, 0, 0]
            ],
            "description": "Perfect corner setup - moves should preserve corner structure"
        },
        {
            "name": "Merge Opportunity Test - Should prioritize valuable merges",
            "board": [
                [32, 32, 4, 2],
                [16, 16, 2, 0],
                [8, 8, 0, 0],
                [4, 4, 0, 0]
            ],
            "description": "Multiple merge opportunities - should choose highest value merges"
        },
        {
            "name": "Empty Space Test - Should create more empty tiles",
            "board": [
                [2, 4, 8, 16],
                [4, 8, 16, 32],
                [8, 16, 32, 64],
                [16, 32, 64, 128]
            ],
            "description": "Full board - should prioritize moves that create empty space"
        },
        {
            "name": "Monotonicity Test - Should preserve ordered sequences",
            "board": [
                [128, 64, 32, 16],
                [64, 32, 16, 8],
                [32, 16, 8, 4],
                [16, 8, 4, 2]
            ],
            "description": "Perfect monotonic board - should preserve the pattern"
        }
    ]

    for i, test in enumerate(test_cases):
        print(f"🧪 Test {i+1}: {test['name']}")
        print(f"   📝 {test['description']}")
        board = test['board']

        # Print the board
        print("   Board state:")
        for row in board:
            print(f"     {row}")

        # Test enhanced heuristic scoring
        scores = strategy.get_move_scores(board)
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]

        print("   🎯 Enhanced Heuristic Move Scores:")
        scored_moves = []
        for j, direction in enumerate(directions):
            score = scores[j]
            if score > -999:
                scored_moves.append((direction, score))
            print(f"     {direction:>5}: {score:10.1f}")

        # Get recommendation
        recommended = strategy.recommend_move(board)
        print(f"   🏆 Recommended: {recommended}")

        # Show best move reasoning
        if scored_moves:
            best_move, best_score = max(scored_moves, key=lambda x: x[1])
            print(f"   ✅ Best move: {best_move} (score: {best_score:.1f})")

        print("")

def test_heuristic_components():
    """Test individual heuristic components to understand scoring"""
    print("🔬 HEURISTIC COMPONENTS ANALYSIS")
    print("=" * 40)

    strategy = BasicStrategy()

    # Test board with clear heuristic features
    test_board = [
        [64, 32, 16, 8],   # Good monotonicity
        [32, 16, 8, 4],    # Corner strategy
        [16, 8, 4, 2],     # Potential merges
        [8, 4, 2, 0]       # Empty space
    ]

    print("Test board:")
    for row in test_board:
        print(f"   {row}")

    total_score = strategy.evaluate_board(test_board)
    print(f"\n🎯 Total Board Score: {total_score:.1f}")

    # Break down scoring components
    empty_count = strategy._count_empty_tiles(test_board)
    merge_score = strategy._evaluate_merge_potential(test_board)
    corner_score = strategy._evaluate_corner_strategy(test_board)
    mono_score = strategy._evaluate_monotonicity(test_board)
    max_tile = strategy._get_max_tile(test_board)

    print(f"\n📊 Heuristic Breakdown:")
    print(f"   Empty tiles: {empty_count} × {strategy.weights['empty_tiles']} = {empty_count * strategy.weights['empty_tiles']:.1f}")
    print(f"   Merge potential: {merge_score} × {strategy.weights['merge_potential']} = {merge_score * strategy.weights['merge_potential']:.1f}")
    print(f"   Corner bonus: {corner_score} × {strategy.weights['corner_bonus']} = {corner_score * strategy.weights['corner_bonus']:.1f}")
    print(f"   Monotonicity: {mono_score} × {strategy.weights['monotonicity']} = {mono_score * strategy.weights['monotonicity']:.1f}")
    print(f"   Max tile value: {max_tile} × {strategy.weights['max_tile_value']} = {max_tile * strategy.weights['max_tile_value']:.1f}")

if __name__ == "__main__":
    test_enhanced_strategy()
    print("\n" + "=" * 60)
    test_heuristic_components()
    print(f"\n🎉 ENHANCED STRATEGY TESTING COMPLETE!")
    print("Strategy now uses sophisticated heuristic evaluation instead of simple priorities.")