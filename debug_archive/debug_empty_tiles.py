#!/usr/bin/env python3
"""
Debug script to check empty tile counting
"""

import sys
from pathlib import Path
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.canonical_vision import CanonicalBoardVision
import cv2

def debug_empty_tile_counting():
    """Debug the empty tile counting logic"""
    print("🔍 DEBUGGING EMPTY TILE COUNTING")
    print("=" * 50)

    # Test with a simple board state
    test_board = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 2, 0, 0],
        [0, 0, 2, 0]
    ]

    board_array = np.array(test_board)
    print(f"Test board:")
    for i, row in enumerate(test_board):
        print(f"   Row {i+1}: {row}")

    print(f"\nBoard array shape: {board_array.shape}")
    print(f"Board array:\n{board_array}")

    # Test different counting methods
    method1 = np.sum(board_array == 0)
    method2 = np.count_nonzero(board_array == 0)
    method3 = len(board_array[board_array == 0])

    print(f"\nEmpty tile counting methods:")
    print(f"   np.sum(board == 0): {method1}")
    print(f"   np.count_nonzero(board == 0): {method2}")
    print(f"   len(board[board == 0]): {method3}")

    # Expected: 14 empty tiles (16 total - 2 with values)
    expected = 14
    print(f"   Expected: {expected}")

    # Now test with real vision system
    print(f"\n🔍 Testing with real vision system...")
    vision = CanonicalBoardVision()

    # Load the actual screenshot
    image_path = "/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo/bot_move_000_before.png"
    image = cv2.imread(image_path)

    if image is not None:
        print(f"✅ Loaded image: {image.shape}")

        # Analyze with vision system
        result = vision.analyze_board(image)

        if result['success']:
            board_state = result['board_state']
            print(f"\nVision detected board state:")
            for i, row in enumerate(board_state):
                print(f"   Row {i+1}: {row}")

            # Count empty tiles
            board_array = np.array(board_state)
            empty_count = np.sum(board_array == 0)
            non_zero_count = np.count_nonzero(board_array)

            print(f"\nVision board analysis:")
            print(f"   Board shape: {board_array.shape}")
            print(f"   Empty tiles (zeros): {empty_count}")
            print(f"   Non-empty tiles: {non_zero_count}")
            print(f"   Total tiles: {board_array.size}")
            print(f"   Sum check: {empty_count + non_zero_count}")

        else:
            print(f"❌ Vision analysis failed: {result.get('debug_info', {})}")
    else:
        print(f"❌ Could not load image: {image_path}")

if __name__ == "__main__":
    debug_empty_tile_counting()