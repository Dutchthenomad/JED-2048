#!/usr/bin/env python3
"""
Manual Strategy Verification Tool
Creates clear, human-readable output for independent verification of strategy choices.

Displays board states, move options, and reasoning in formats easy to manually verify.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.strategy import BasicStrategy, Move
from core.improved_vision import ImprovedBoardVision
import cv2

def display_board(board, title="Board State"):
    """Display board in clear visual format"""
    print(f"\\n{title}:")
    print("   ┌─────┬─────┬─────┬─────┐")
    for row in range(4):
        tiles = "   │"
        for col in range(4):
            value = board[row][col]
            if value == 0:
                tiles += "     │"
            else:
                tiles += f"{value:^5}│"
        print(tiles)
        if row < 3:
            print("   ├─────┼─────┼─────┼─────┤")
    print("   └─────┴─────┴─────┴─────┘")

def display_move_analysis(analysis, current_board):
    """Display detailed move analysis for manual verification"""
    print(f"\\n🎯 Strategy Analysis:")
    print(f"   Recommended Move: {analysis['chosen_move'].value}")
    print(f"   Best Score: {analysis['best_score']:.1f}")
    print(f"   Reasoning: {analysis['reasoning']}")

    print(f"\\n📊 All Move Options:")
    print("   " + "─" * 60)

    for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
        move_data = analysis['move_analysis'][move]
        score = analysis['all_scores'][move]
        possible = move_data.get('possible', True)

        status = "✅ POSSIBLE" if possible else "❌ BLOCKED"
        chosen = "👈 CHOSEN" if move == analysis['chosen_move'] else ""

        print(f"   {move.value:>5}: {score:>8.1f} | {status} {chosen}")

        if possible and 'resulting_board' in move_data:
            print(f"          → {move_data['empty_tiles']} empty tiles after move")

    print("   " + "─" * 60)

def simulate_and_show_moves(strategy, board):
    """Show what happens with each possible move"""
    print(f"\\n🔍 Move Simulation Preview:")

    for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
        result_board = strategy._simulate_move(board, move)

        if result_board is None:
            print(f"\\n   {move.value}: ❌ No tiles can move")
        else:
            empty_count = strategy._count_empty_tiles(result_board)
            print(f"\\n   {move.value}: ✅ Results in {empty_count} empty tiles")

            # Show resulting board in compact format
            print("   Result: ", end="")
            for row in range(4):
                if row > 0:
                    print("\\n           ", end="")
                print("[", end="")
                for col in range(4):
                    value = result_board[row][col]
                    print(f"{value:3d}", end="")
                    if col < 3:
                        print(",", end="")
                print("]", end="")
            print()

def explain_heuristics(strategy, board):
    """Explain heuristic calculations for manual verification"""
    print(f"\\n🧮 Heuristic Breakdown:")

    # Empty tiles
    empty_count = strategy._count_empty_tiles(board)
    empty_score = empty_count * strategy.weights['empty_tiles']
    print(f"   Empty Tiles: {empty_count} × {strategy.weights['empty_tiles']} = {empty_score:.1f}")

    # Merge potential
    merge_potential = strategy._evaluate_merge_potential(board)
    merge_score = merge_potential * strategy.weights['merge_potential']
    print(f"   Merge Potential: {merge_potential} × {strategy.weights['merge_potential']} = {merge_score:.1f}")

    # Corner strategy
    corner_bonus = strategy._evaluate_corner_strategy(board)
    corner_score = corner_bonus * strategy.weights['corner_bonus']
    max_tile = strategy._get_max_tile(board)
    print(f"   Corner Strategy: {corner_bonus} × {strategy.weights['corner_bonus']} = {corner_score:.1f} (max tile: {max_tile})")

    # Monotonicity
    mono_bonus = strategy._evaluate_monotonicity(board)
    mono_score = mono_bonus * strategy.weights['monotonicity']
    print(f"   Monotonicity: {mono_bonus:.1f} × {strategy.weights['monotonicity']} = {mono_score:.1f}")

    # Max tile value
    max_value_score = max_tile * strategy.weights['max_tile_value']
    print(f"   Max Tile Value: {max_tile} × {strategy.weights['max_tile_value']} = {max_value_score:.1f}")

    total_score = strategy.evaluate_board(board)
    print(f"   ═══════════════════════════════════════")
    print(f"   Total Board Score: {total_score:.1f}")

def manual_verification_session(image_path):
    """Run interactive manual verification session"""
    print("🔍 Manual Strategy Verification")
    print("=" * 50)

    # Load and analyze image
    print(f"📁 Loading: {image_path.name}")

    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        return

    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Extract board state
    vision = ImprovedBoardVision()
    vision_results = vision.analyze_board(image)

    if not vision_results['success']:
        print(f"❌ Vision analysis failed: {vision_results.get('debug_info', {}).get('error')}")
        return

    board = vision_results['board_state']
    print(f"✅ Board extracted from screenshot")

    # Display current board
    display_board(board, "Current Board State")

    # Initialize strategy
    strategy = BasicStrategy(debug_mode=False)

    # Get strategy recommendation
    best_move, analysis = strategy.get_best_move(board)

    # Display analysis
    display_move_analysis(analysis, board)

    # Show heuristic breakdown
    explain_heuristics(strategy, board)

    # Show move simulations
    simulate_and_show_moves(strategy, board)

    print(f"\\n💡 Manual Verification Checklist:")
    print(f"   1. Does the recommended move ({best_move.value}) make sense?")
    print(f"   2. Are the move scores reasonable compared to each other?")
    print(f"   3. Do the heuristic calculations look correct?")
    print(f"   4. Would you choose the same move or a different one?")

    return {
        "board": board,
        "recommended_move": best_move,
        "analysis": analysis,
        "image_source": str(image_path)
    }

def main():
    """Run manual verification on all available screenshots"""
    print("🎮 Manual Strategy Verification Tool")
    print("=" * 50)
    print("Interactive verification of strategy choices")
    print("Uses real screenshot data for validation\\n")

    # Find available screenshots
    screenshots_dir = project_root / "validation_data" / "easy_captures"
    screenshots = list(screenshots_dir.glob("*.png"))

    if not screenshots:
        print("❌ No screenshots found in validation_data/easy_captures/")
        return

    print("📸 Available Screenshots:")
    for i, screenshot in enumerate(screenshots, 1):
        print(f"   {i}. {screenshot.name}")

    # Verify each screenshot
    for i, screenshot in enumerate(screenshots, 1):
        print(f"\\n{'='*60}")
        print(f"VERIFICATION SESSION {i}/{len(screenshots)}")
        print(f"{'='*60}")

        result = manual_verification_session(screenshot)

        if i < len(screenshots):
            input("\\nPress Enter to continue to next screenshot...")

    print(f"\\n🎉 Manual verification completed!")
    print(f"   Reviewed {len(screenshots)} scenarios")
    print(f"   All strategy choices ready for your independent verification")

if __name__ == "__main__":
    main()