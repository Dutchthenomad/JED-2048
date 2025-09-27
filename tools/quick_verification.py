#!/usr/bin/env python3
"""
Quick Strategy Verification
Non-interactive version for batch verification of all screenshots.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.strategy import BasicStrategy, Move
from core.improved_vision import ImprovedBoardVision
import cv2

def display_board_compact(board, title="Board"):
    """Display board in compact format"""
    print(f"{title}:")
    for row in board:
        print("   [" + ", ".join(f"{tile:3d}" for tile in row) + "]")

def quick_verification(image_path):
    """Quick verification of strategy for one screenshot"""
    print(f"\n📁 {image_path.name}")
    print("─" * 50)

    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ Could not load image")
        return

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Extract board
    vision = ImprovedBoardVision()
    vision_results = vision.analyze_board(image)

    if not vision_results['success']:
        print(f"❌ Vision failed: {vision_results.get('debug_info', {}).get('error', 'Unknown')}")
        return

    board = vision_results['board_state']

    # Analyze strategy
    strategy = BasicStrategy(debug_mode=False)
    best_move, analysis = strategy.get_best_move(board)

    # Display results
    display_board_compact(board, "Board State")

    print(f"\n🎯 Strategy Decision:")
    print(f"   Recommended: {best_move.value} (score: {analysis['best_score']:.1f})")

    print(f"\n📊 Move Scores:")
    for move in [Move.UP, Move.DOWN, Move.LEFT, Move.RIGHT]:
        score = analysis['all_scores'][move]
        possible = analysis['move_analysis'][move].get('possible', True)
        marker = "👈" if move == best_move else "  "
        status = "✅" if possible else "❌"
        print(f"      {status} {move.value:>5}: {score:>8.1f} {marker}")

    # Key metrics
    empty_tiles = strategy._count_empty_tiles(board)
    max_tile = strategy._get_max_tile(board)
    print(f"\n📈 Key Metrics:")
    print(f"   Empty tiles: {empty_tiles}/16")
    print(f"   Max tile: {max_tile}")
    print(f"   Corner strategy: {strategy._evaluate_corner_strategy(board):.1f}")

def main():
    print("⚡ Quick Strategy Verification")
    print("=" * 50)
    print("Batch verification of all screenshots\n")

    # Find screenshots
    screenshots_dir = project_root / "validation_data" / "easy_captures"
    screenshots = sorted(screenshots_dir.glob("*.png"))

    if not screenshots:
        print("❌ No screenshots found")
        return

    print(f"Found {len(screenshots)} screenshots")

    # Process each screenshot
    for screenshot in screenshots:
        quick_verification(screenshot)

    print(f"\n✅ Verification complete!")
    print(f"Analyzed {len(screenshots)} scenarios")

if __name__ == "__main__":
    main()