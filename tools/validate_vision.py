#!/usr/bin/env python3
"""
Quick validation of improved vision system results
Validates against the actual user-labeled board states
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.improved_vision import ImprovedBoardVision
import cv2

def main():
    print("🎯 Vision System Validation")
    print("=" * 40)

    # User-labeled board states
    expected_boards = {
        "2048_capture_20250917_222936_01.png": {
            "board": [[2,8,4,2], [2,8,64,32], [32,128,8,4], [4,32,16,2]],
            "description": "Mature game state"
        },
        "2048_capture_20250917_223121_01.png": {
            "board": [[2,4,16,2], [8,16,32,4], [16,256,4,32], [2,8,64,2]],
            "description": "Game over screen (has 256 tile)"
        }
    }

    vision = ImprovedBoardVision()

    for image_name, expected in expected_boards.items():
        print(f"\n📁 Testing: {image_name}")
        print(f"📋 {expected['description']}")

        # Load image
        image_path = project_root / "validation_data" / "easy_captures" / image_name
        image = cv2.imread(str(image_path))

        if image is None:
            print(f"❌ Could not load image: {image_path}")
            continue

        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Analyze
        results = vision.analyze_board(image, save_debug=True)

        if not results['success']:
            print(f"❌ Analysis failed: {results.get('debug_info', {}).get('error', 'Unknown')}")
            continue

        detected = results['board_state']
        expected_board = expected['board']

        # Compare boards
        matches = 0
        total = 16

        print("\n🔍 Comparison:")
        print("   Expected vs Detected")
        for row in range(4):
            exp_row = "   [" + ", ".join(f"{expected_board[row][col]:3d}" for col in range(4)) + "]"
            det_row = " vs [" + ", ".join(f"{detected[row][col]:3d}" for col in range(4)) + "]"
            print(exp_row + det_row)

            for col in range(4):
                if expected_board[row][col] == detected[row][col]:
                    matches += 1

        accuracy = (matches / total) * 100
        print(f"\n✅ Accuracy: {accuracy:.1f}% ({matches}/{total} tiles correct)")

        # Check for specific issues
        if accuracy < 100:
            print("\n🔍 Differences found:")
            for row in range(4):
                for col in range(4):
                    if expected_board[row][col] != detected[row][col]:
                        pos = chr(65 + row) + str(col + 1)
                        print(f"   {pos}: Expected {expected_board[row][col]}, Got {detected[row][col]}")

if __name__ == "__main__":
    main()