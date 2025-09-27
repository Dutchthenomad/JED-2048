#!/usr/bin/env python3
"""
Vision System Test Tool
Tests board detection and tile recognition on real captured screenshots.

Usage:
    python tools/test_vision.py [screenshot_path]
"""

import sys
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.vision import BoardVision

def test_vision_on_screenshot(image_path: str, save_debug: bool = True):
    """
    Test vision system on real screenshot

    Args:
        image_path: Path to real captured screenshot
        save_debug: Save debug images showing analysis steps
    """

    print("🔍 2048 Vision System Test")
    print("=" * 35)
    print(f"📁 Image: {Path(image_path).name}")

    # Load real screenshot
    try:
        # Load image (OpenCV loads as BGR)
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            print(f"❌ Could not load image: {image_path}")
            return False

        # Convert to RGB for processing
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        height, width = image_rgb.shape[:2]

        print(f"✅ Image loaded: {width}x{height}")

    except Exception as e:
        print(f"❌ Image loading failed: {e}")
        return False

    # Initialize vision system
    try:
        vision = BoardVision()
        print("✅ Vision system initialized")

    except Exception as e:
        print(f"❌ Vision system initialization failed: {e}")
        return False

    # Run complete analysis
    print(f"\n🔍 Analyzing board...")

    try:
        results = vision.analyze_board(image_rgb, save_debug=save_debug)

        # Display results
        print(f"\n📊 Analysis Results:")
        print(f"   ✅ Success: {results['success']}")
        print(f"   🎯 Board detected: {results['board_detected']}")
        print(f"   📏 Grid extracted: {results['grid_extracted']}")

        if results['board_region']:
            x, y, w, h = results['board_region']
            print(f"   📍 Board region: ({x}, {y}) size {w}x{h}")

        # Show board state
        if results['success']:
            print(f"\n🎮 Detected Board State:")
            board = results['board_state']

            # Print board in nice format
            print("   ┌─────┬─────┬─────┬─────┐")
            for row in range(4):
                row_str = "   │"
                for col in range(4):
                    value = board[row][col]
                    if value == 0:
                        cell = "     "
                    else:
                        cell = f"{value:^5}"
                    row_str += cell + "│"
                print(row_str)
                if row < 3:
                    print("   ├─────┼─────┼─────┼─────┤")
            print("   └─────┴─────┴─────┴─────┘")

            # Count tiles
            non_empty = sum(1 for row in board for tile in row if tile > 0)
            max_tile = max(max(row) for row in board) if non_empty > 0 else 0

            print(f"\n📈 Board Statistics:")
            print(f"   🎯 Non-empty tiles: {non_empty}/16")
            print(f"   🏆 Highest tile: {max_tile}")

            # Show confidence scores
            confidence = results['confidence_scores']
            avg_confidence = np.mean(confidence)
            print(f"   🎯 Average confidence: {avg_confidence:.2f}")

        else:
            error = results.get('debug_info', {}).get('error', 'Unknown error')
            print(f"   ❌ Analysis failed: {error}")

        # Debug images info
        if save_debug:
            debug_dir = project_root / "validation_data" / "debug_vision"
            if debug_dir.exists():
                debug_files = list(debug_dir.glob("debug_*.png"))
                if debug_files:
                    print(f"\n🖼️  Debug images saved:")
                    for file in sorted(debug_files)[-3:]:  # Show last 3
                        print(f"   📁 {file.name}")
                    print(f"   📂 Location: {debug_dir}")

        # Summary
        summary = vision.get_analysis_summary()
        print(f"\n📋 Summary:")
        for line in summary.split('\n'):
            if line.strip():
                print(f"   {line}")

        return results['success']

    except Exception as e:
        print(f"❌ Vision analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""

    print("🚀 2048 Vision System - Real Screenshot Analysis")
    print("=" * 55)

    # Find available screenshots
    validation_dir = project_root / "validation_data"
    screenshots = []

    for subdir in validation_dir.iterdir():
        if subdir.is_dir():
            screenshots.extend(subdir.glob("*.png"))

    if len(sys.argv) > 1:
        # User specified screenshot
        image_path = sys.argv[1]
        if not Path(image_path).exists():
            print(f"❌ Image not found: {image_path}")
            return
    else:
        # Auto-select most recent screenshot
        if not screenshots:
            print("❌ No screenshots found in validation_data/")
            print("   Run python tools/easy_capture.py first to capture a screenshot")
            return

        # Use most recent screenshot
        image_path = max(screenshots, key=lambda p: p.stat().st_mtime)
        print(f"🔄 Auto-selected most recent screenshot: {image_path.name}")

    # Test vision system
    success = test_vision_on_screenshot(str(image_path), save_debug=True)

    if success:
        print(f"\n🎉 Vision system test completed successfully!")
        print(f"   The system can detect and analyze real 2048 game boards.")
    else:
        print(f"\n🔧 Vision system needs improvement.")
        print(f"   Check debug images and error messages above.")

    print(f"\n💡 Next steps:")
    print(f"   1. Review debug images to see detection accuracy")
    print(f"   2. Test with different game states (more tiles)")
    print(f"   3. Refine recognition algorithms if needed")

if __name__ == "__main__":
    main()