#!/usr/bin/env python3
"""
Canonical Color-Based Vision Test
Implementation using definitive 2048game.com hex color values.
Tests 100% accuracy on provided screenshots before bot integration.
"""

import sys
from pathlib import Path
import cv2
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Canonical 2048 hex colors from 2048game.com
HEX_COLORS = {
    "2": "#eee4da",
    "4": "#ede0c8",
    "8": "#f2b179",
    "16": "#f59563",
    "32": "#f67c5f",
    "64": "#f65e3b",
    "128": "#edcf72",
    "256": "#edcc61",
    "512": "#edc850",
    "1024": "#edc53f",
    "2048": "#edc22e"
}

# Special backgrounds
EMPTY_COLOR = "#cdc1b4"  # Empty cell background
BOARD_COLOR = "#bbada0"  # Board background

def hex_to_bgr(hex_color):
    """Convert hex color to BGR tuple for OpenCV"""
    hex_color = hex_color.lstrip('#')
    # Convert hex to RGB, then swap to BGR for OpenCV
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)  # BGR format for OpenCV

def setup_color_database():
    """Create BGR color database from canonical hex values"""
    bgr_colors = {}

    # Convert tile colors
    for value, hex_color in HEX_COLORS.items():
        bgr_colors[int(value)] = np.array(hex_to_bgr(hex_color), dtype=np.uint8)

    # Add special colors
    bgr_colors[0] = np.array(hex_to_bgr(EMPTY_COLOR), dtype=np.uint8)  # Empty cells
    bgr_colors["board"] = np.array(hex_to_bgr(BOARD_COLOR), dtype=np.uint8)  # Board background

    return bgr_colors

def classify_tile_patch(patch_bgr, bgr_database, tolerance=25):
    """
    Classify a tile patch using canonical colors with distance matching

    Args:
        patch_bgr: BGR image patch of the tile
        bgr_database: Dictionary of tile_value -> BGR color
        tolerance: Maximum color distance for valid match

    Returns:
        (tile_value, confidence_score)
    """
    if patch_bgr is None or patch_bgr.size == 0:
        return 0, 0.0

    # Sample center 60% of patch to avoid borders/shadows
    h, w = patch_bgr.shape[:2]
    margin_h, margin_w = int(h * 0.2), int(w * 0.2)
    center_patch = patch_bgr[margin_h:h-margin_h, margin_w:w-margin_w]

    if center_patch.size == 0:
        center_patch = patch_bgr  # Fallback to full patch

    # Use median color for robustness against noise/gradients
    median_color = np.median(center_patch.reshape(-1, 3), axis=0).astype(np.uint8)

    # Find nearest color match
    best_match = 0
    best_distance = float('inf')

    # Test tile colors (excluding board background)
    for tile_value, target_color in bgr_database.items():
        if tile_value == "board":
            continue

        # Calculate L2 distance in BGR space
        distance = np.linalg.norm(median_color.astype(np.int16) - target_color.astype(np.int16))

        if distance < best_distance:
            best_distance = distance
            best_match = tile_value

    # Check if match is within tolerance
    if best_distance <= tolerance:
        confidence = max(0, 1 - (best_distance / tolerance))
        return best_match, confidence
    else:
        # No good match found
        return 0, 0.0

def analyze_screenshot_with_canonical_colors(image_path, expected_board=None):
    """
    Analyze a 2048 screenshot using canonical color matching

    Args:
        image_path: Path to screenshot
        expected_board: Optional 4x4 array of expected values for validation

    Returns:
        Dictionary with detected board state and accuracy info
    """
    print(f"\n🔍 Analyzing: {Path(image_path).name}")

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Could not load: {image_path}")
        return None

    print(f"📏 Image size: {image.shape}")

    # Setup color database
    bgr_db = setup_color_database()

    # Import board detection from existing vision system
    from core.improved_vision import ImprovedBoardVision
    temp_vision = ImprovedBoardVision()

    # Detect board region
    board_region = temp_vision.detect_board_region(image)
    if not board_region:
        print("❌ Board region not detected")
        return None

    print(f"✅ Board region: {board_region}")

    # Extract board image
    x, y, w, h = board_region
    board_image = image[y:y+h, x:x+w]

    # Create 4x4 grid
    tile_h, tile_w = h // 4, w // 4
    detected_board = [[0 for _ in range(4)] for _ in range(4)]
    confidence_grid = [[0.0 for _ in range(4)] for _ in range(4)]

    print("🎯 Tile-by-tile analysis:")

    for row in range(4):
        for col in range(4):
            # Extract tile patch
            ty1 = row * tile_h
            ty2 = (row + 1) * tile_h
            tx1 = col * tile_w
            tx2 = (col + 1) * tile_w

            tile_patch = board_image[ty1:ty2, tx1:tx2]

            # Classify using canonical colors
            tile_value, confidence = classify_tile_patch(tile_patch, bgr_db)
            detected_board[row][col] = tile_value
            confidence_grid[row][col] = confidence

            # Get expected value for comparison
            expected_val = expected_board[row][col] if expected_board else "?"
            match_status = "✅" if (expected_board is None or tile_value == expected_val) else "❌"

            print(f"   {chr(65+row)}{col+1}: Detected={tile_value:>4}, Expected={expected_val:>4}, Conf={confidence:.2f} {match_status}")

    # Calculate accuracy if expected board provided
    accuracy = None
    if expected_board:
        correct = sum(1 for row in range(4) for col in range(4)
                     if detected_board[row][col] == expected_board[row][col])
        accuracy = correct / 16
        print(f"\n📊 Accuracy: {correct}/16 = {accuracy:.1%}")

    return {
        'detected_board': detected_board,
        'confidence_grid': confidence_grid,
        'accuracy': accuracy,
        'board_region': board_region
    }

def test_provided_screenshots():
    """Test canonical color system on provided screenshots"""
    print("🚀 Testing Canonical Color Vision System")
    print("=" * 60)

    # Test data using available screenshots
    test_screenshots = [
        {
            "file": "/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo/bot_move_000_before.png",
            "expected": [
                [0, 0, 0, 0],
                [2, 0, 0, 0],
                [0, 0, 0, 0],
                [2, 0, 0, 0]
            ]
        },
        {
            "file": "/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo/init_check.png",
            "expected": [
                [0, 0, 0, 0],
                [2, 0, 0, 0],
                [0, 0, 0, 0],
                [2, 0, 0, 0]
            ]
        }
    ]

    results = []
    total_accuracy = 0

    for test_data in test_screenshots:
        file_path = test_data["file"]
        expected_board = test_data["expected"]

        if not Path(file_path).exists():
            print(f"⚠️  File not found: {Path(file_path).name}")
            continue

        result = analyze_screenshot_with_canonical_colors(file_path, expected_board)
        if result:
            results.append(result)
            if result['accuracy'] is not None:
                total_accuracy += result['accuracy']

    # Overall results
    if results:
        avg_accuracy = total_accuracy / len(results)
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   📊 Average accuracy: {avg_accuracy:.1%}")
        print(f"   📈 Screenshots tested: {len(results)}")

        if avg_accuracy >= 1.0:
            print(f"   🎉 PERFECT ACCURACY ACHIEVED!")
            print(f"   ✅ Ready for bot integration")
        elif avg_accuracy >= 0.9:
            print(f"   ✅ Excellent accuracy - minor tuning may help")
        else:
            print(f"   ⚠️  Needs improvement - check color matching")

        return avg_accuracy >= 0.95
    else:
        print("❌ No valid results")
        return False

def main():
    """Main test function"""
    print("🎯 Canonical Color-Based Vision System Test")

    success = test_provided_screenshots()

    if success:
        print("\n✅ CANONICAL COLOR SYSTEM VALIDATED!")
        print("🚀 Ready to integrate with complete 2048 bot")
    else:
        print("\n🔧 System needs refinement before bot integration")

    return success

if __name__ == "__main__":
    main()