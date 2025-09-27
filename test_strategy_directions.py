#!/usr/bin/env python3
"""
Test script to validate strategy system can detect and recommend all four directions
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.strategy import BasicStrategy

def test_all_directions():
    """Test that strategy can recommend all four directions in different scenarios"""
    print("🧠 STRATEGY DIRECTION VALIDATION TEST")
    print("=" * 60)

    strategy = BasicStrategy()

    # Test scenarios where each direction should be optimal
    test_cases = [
        {
            "name": "Empty board with tiles on LEFT - should recommend RIGHT",
            "board": [
                [2, 0, 0, 0],
                [2, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            "expected_not": "LEFT"  # Should NOT recommend LEFT
        },
        {
            "name": "Tiles on RIGHT side - should recommend LEFT",
            "board": [
                [0, 0, 0, 2],
                [0, 0, 0, 4],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            "expected_not": "RIGHT"  # Should NOT recommend RIGHT
        },
        {
            "name": "Tiles on TOP - should recommend DOWN",
            "board": [
                [2, 4, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            "expected_not": "UP"  # Should NOT recommend UP
        },
        {
            "name": "Tiles on BOTTOM - should recommend UP",
            "board": [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [2, 4, 0, 0]
            ],
            "expected_not": "DOWN"  # Should NOT recommend DOWN
        },
        {
            "name": "Board where RIGHT is blocked",
            "board": [
                [2, 4, 8, 16],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            "expected_not": "RIGHT"  # RIGHT should be invalid/low priority
        }
    ]

    for i, test in enumerate(test_cases):
        print(f"\n🧪 Test {i+1}: {test['name']}")
        board = test['board']

        # Print the board
        print("   Board state:")
        for row in board:
            print(f"     {row}")

        # Test get_move_scores
        scores = strategy.get_move_scores(board)
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]

        print("   Move scores:")
        for j, direction in enumerate(directions):
            score = scores[j]
            print(f"     {direction:>5}: {score:8.1f}")

        # Test recommend_move
        recommended = strategy.recommend_move(board)
        print(f"   🎯 Recommended: {recommended}")

        # Check if recommendation makes sense
        if "expected_not" in test:
            if recommended == test["expected_not"]:
                print(f"   ❌ FAIL: Should NOT recommend {test['expected_not']}")
            else:
                print(f"   ✅ PASS: Correctly avoided {test['expected_not']}")

        # Check that recommended move has valid score
        rec_index = directions.index(recommended)
        rec_score = scores[rec_index]
        if rec_score > -999:
            print(f"   ✅ Recommended move is valid (score: {rec_score})")
        else:
            print(f"   ❌ FAIL: Recommended invalid move (score: {rec_score})")

def test_priority_system():
    """Test that priority system works as expected"""
    print(f"\n🎯 PRIORITY SYSTEM TEST")
    print("=" * 30)

    strategy = BasicStrategy()

    # Test with board where all moves are valid
    board = [
        [0, 2, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 2]
    ]

    print("Board where all moves should be valid:")
    for row in board:
        print(f"   {row}")

    scores = strategy.get_move_scores(board)
    directions = ["UP", "DOWN", "LEFT", "RIGHT"]

    print("\nMove scores (should show priority: UP > LEFT > DOWN > RIGHT):")
    for i, direction in enumerate(directions):
        score = scores[i]
        print(f"   {direction:>5}: {score:8.1f}")

    recommended = strategy.recommend_move(board)
    print(f"\n🎯 Recommended: {recommended}")

    # UP should be highest priority (4.0)
    if scores[0] == 4.0:  # UP
        print("   ✅ UP has correct priority (4.0)")
    else:
        print(f"   ❌ UP has wrong priority ({scores[0]}, expected 4.0)")

    # Recommended should be UP if all moves are valid
    if recommended == "UP":
        print("   ✅ Correctly recommends highest priority move (UP)")
    else:
        print(f"   ❌ Should recommend UP but got {recommended}")

if __name__ == "__main__":
    test_all_directions()
    test_priority_system()

    print(f"\n🎉 STRATEGY VALIDATION COMPLETE!")
    print("If all tests pass, strategy system is working correctly.")