#!/usr/bin/env python3
"""
Improved Vision System Test
Compares original vs trained vision system on real screenshots.

Usage:
    python tools/test_improved_vision.py [screenshot_path]
"""

import sys
import cv2
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.vision import BoardVision
from core.improved_vision import ImprovedBoardVision

def compare_vision_systems(image_path: str, expected_board: list = None):
    """
    Compare original vs improved vision systems on real screenshot

    Args:
        image_path: Path to real screenshot
        expected_board: Known correct board state (if available)
    """

    print("🔍 Vision System Comparison")
    print("=" * 35)
    print(f"📁 Image: {Path(image_path).name}")

    # Load real screenshot
    try:
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            print(f"❌ Could not load image: {image_path}")
            return False

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        height, width = image_rgb.shape[:2]
        print(f"✅ Image loaded: {width}x{height}")

    except Exception as e:
        print(f"❌ Image loading failed: {e}")
        return False

    # Initialize both vision systems
    try:
        original_vision = BoardVision()
        improved_vision = ImprovedBoardVision()
        print("✅ Vision systems initialized")

    except Exception as e:
        print(f"❌ Vision system initialization failed: {e}")
        return False

    # Test original vision system
    print(f"\n🔍 Testing Original Vision System...")
    try:
        original_results = original_vision.analyze_board(image_rgb, save_debug=True)
        print(f"   ✅ Original analysis completed")
    except Exception as e:
        print(f"   ❌ Original analysis failed: {e}")
        original_results = None

    # Test improved vision system
    print(f"\n🧠 Testing Improved Vision System...")
    try:
        improved_results = improved_vision.analyze_board(image_rgb, save_debug=True)
        print(f"   ✅ Improved analysis completed")
    except Exception as e:
        print(f"   ❌ Improved analysis failed: {e}")
        improved_results = None

    # Compare results
    print(f"\n📊 Results Comparison:")
    print(f"=" * 25)

    # Success rates
    original_success = original_results['success'] if original_results else False
    improved_success = improved_results['success'] if improved_results else False

    print(f"🎯 Success Rate:")
    print(f"   Original:  {'✅' if original_success else '❌'}")
    print(f"   Improved:  {'✅' if improved_success else '❌'}")

    # Board detection
    if original_results and improved_results:
        print(f"\n📍 Board Detection:")
        print(f"   Original:  {original_results['board_region']}")
        print(f"   Improved:  {improved_results['board_region']}")

        # Board state comparison
        print(f"\n🎮 Detected Board States:")

        original_board = original_results['board_state']
        improved_board = improved_results['board_state']

        print(f"   📋 Original System:")
        print_board(original_board)

        print(f"\n   🧠 Improved System:")
        print_board(improved_board)

        # Expected board (if provided)
        if expected_board:
            print(f"\n   🎯 Expected (User Labels):")
            print_board(expected_board)

            # Accuracy calculation
            original_accuracy = calculate_accuracy(original_board, expected_board)
            improved_accuracy = calculate_accuracy(improved_board, expected_board)

            print(f"\n📈 Accuracy vs Expected:")
            print(f"   Original:  {original_accuracy:.1%}")
            print(f"   Improved:  {improved_accuracy:.1%}")

            if improved_accuracy > original_accuracy:
                print(f"   🎉 Improved system is {improved_accuracy - original_accuracy:.1%} more accurate!")
            elif original_accuracy > improved_accuracy:
                print(f"   ⚠️  Original system was {original_accuracy - improved_accuracy:.1%} more accurate")
            else:
                print(f"   ⚖️  Both systems performed equally")

        # Confidence scores
        original_conf = np.mean(original_results['confidence_scores'])
        improved_conf = np.mean(improved_results['confidence_scores'])

        print(f"\n🎯 Average Confidence:")
        print(f"   Original:  {original_conf:.2f}")
        print(f"   Improved:  {improved_conf:.2f}")

        # Non-empty tile counts
        original_tiles = count_non_empty(original_board)
        improved_tiles = count_non_empty(improved_board)

        print(f"\n🔢 Non-empty Tiles Detected:")
        print(f"   Original:  {original_tiles}/16")
        print(f"   Improved:  {improved_tiles}/16")

        if expected_board:
            expected_tiles = count_non_empty(expected_board)
            print(f"   Expected:  {expected_tiles}/16")

    # Debug images
    debug_original = project_root / "validation_data" / "debug_vision"
    debug_improved = project_root / "validation_data" / "debug_improved"

    print(f"\n🖼️  Debug Images:")
    print(f"   Original: {debug_original}")
    print(f"   Improved: {debug_improved}")

    return True

def print_board(board: list):
    """Print board in nice format"""
    print("      ┌─────┬─────┬─────┬─────┐")
    for row in range(4):
        row_str = "      │"
        for col in range(4):
            value = board[row][col]
            if value == 0:
                cell = "     "
            else:
                cell = f"{value:^5}"
            row_str += cell + "│"
        print(row_str)
        if row < 3:
            print("      ├─────┼─────┼─────┼─────┤")
    print("      └─────┴─────┴─────┴─────┘")

def calculate_accuracy(detected: list, expected: list) -> float:
    """Calculate accuracy percentage between detected and expected boards"""
    correct = 0
    total = 16

    for row in range(4):
        for col in range(4):
            if detected[row][col] == expected[row][col]:
                correct += 1

    return correct / total

def count_non_empty(board: list) -> int:
    """Count non-empty tiles in board"""
    return sum(1 for row in board for tile in row if tile > 0)

def main():
    """Main comparison function"""

    print("🚀 2048 Vision System Comparison")
    print("=" * 45)
    print("Comparing original vs improved vision systems")
    print("Using real screenshots and known labels\n")

    # Expected board state from user's manual labeling
    expected_board = [
        [4,  2,  16, 0 ],  # Row A
        [16, 4,  2,  0 ],  # Row B
        [4,  32, 0,  0 ],  # Row C
        [16, 0,  0,  2 ]   # Row D
    ]

    # Use labeled screenshot by default
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use the labeled screenshot
        image_path = project_root / "validation_data" / "easy_captures" / "2048_capture_20250917_221057_01.png"

    if not Path(image_path).exists():
        print(f"❌ Screenshot not found: {image_path}")
        return

    print(f"📁 Testing with: {Path(image_path).name}")
    print(f"🏷️  Using manual labels as ground truth")

    # Run comparison
    success = compare_vision_systems(str(image_path), expected_board)

    if success:
        print(f"\n🎉 Vision system comparison completed!")
        print(f"   Check debug images to see detection differences")
        print(f"   Review accuracy metrics above")
    else:
        print(f"\n🔧 Comparison failed")

    print(f"\n💡 Next steps:")
    print(f"   1. Review debug images for visual comparison")
    print(f"   2. Test on additional screenshots")
    print(f"   3. Fine-tune recognition if needed")

if __name__ == "__main__":
    main()