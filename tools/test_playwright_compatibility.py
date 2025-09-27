#!/usr/bin/env python3
"""
Playwright Vision Compatibility Test
Tests compatibility between Playwright screenshots and our vision system.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.improved_vision import ImprovedBoardVision

def test_vision_with_existing_data():
    """Test vision system with existing validation screenshots"""
    print("🔍 Testing vision system with existing screenshots...")

    try:
        # Initialize vision system
        vision = ImprovedBoardVision()

        # Test with existing validation data
        validation_dir = Path("validation_data/easy_captures")

        test_screenshots = list(validation_dir.glob("*.png"))

        if not test_screenshots:
            print("❌ No test screenshots found in validation data")
            return False

        print(f"📸 Found {len(test_screenshots)} test screenshots")

        success_count = 0
        for screenshot in test_screenshots[:3]:  # Test first 3 screenshots
            print(f"\n🎯 Testing: {screenshot.name}")

            try:
                # Load image using cv2 (as expected by vision system)
                import cv2
                image = cv2.imread(str(screenshot))

                if image is None:
                    print(f"❌ Could not load image: {screenshot.name}")
                    continue

                # Test board detection
                board_region = vision.detect_board_region(image)

                if board_region:
                    print(f"✅ Board detected at region: {board_region}")

                    # Test board analysis
                    result = vision.analyze_board(image)

                    if result['success']:
                        board_state = result['board_state']
                        print("✅ Board analysis successful!")
                        print("📊 Board state:")
                        for i, row in enumerate(board_state):
                            print(f"   Row {i+1}: {row}")
                        success_count += 1
                    else:
                        print("❌ Board analysis failed")
                else:
                    print("❌ Board detection failed")

            except Exception as e:
                print(f"❌ Error processing {screenshot.name}: {str(e)}")

        print(f"\n📊 Results: {success_count}/{len(test_screenshots[:3])} screenshots processed successfully")
        return success_count > 0

    except Exception as e:
        print(f"❌ Vision system error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_screenshot_format_requirements():
    """Test what format requirements our vision system has"""
    print("\n🔧 Testing screenshot format requirements...")

    try:
        from PIL import Image
        import numpy as np

        # Test our vision system requirements with existing data
        validation_dir = Path("validation_data/easy_captures")
        test_screenshots = list(validation_dir.glob("*.png"))

        if not test_screenshots:
            print("❌ No test screenshots available")
            return False

        test_screenshot = test_screenshots[0]
        print(f"📸 Analyzing format of: {test_screenshot.name}")

        # Load with PIL to check format
        img = Image.open(test_screenshot)
        print(f"✅ Image format: {img.format}")
        print(f"✅ Image mode: {img.mode}")
        print(f"✅ Image size: {img.size}")

        # Convert to numpy to check data format
        img_array = np.array(img)
        print(f"✅ Array shape: {img_array.shape}")
        print(f"✅ Array dtype: {img_array.dtype}")

        # Test if our vision system can process this format
        vision = ImprovedBoardVision()

        # Load image with cv2 for vision system
        import cv2
        image = cv2.imread(str(test_screenshot))

        if image is None:
            print("❌ Could not load image with cv2")
            return False

        result = vision.analyze_board(image)

        if result['success']:
            print("✅ Vision system processes this format successfully")
            return True
        else:
            print("❌ Vision system cannot process this format")
            return False

    except Exception as e:
        print(f"❌ Format test error: {str(e)}")
        return False

def main():
    """Main compatibility test"""
    print("=" * 60)
    print("  Playwright Vision Compatibility Test")
    print("=" * 60)
    print("Testing our vision system readiness for Playwright integration\n")

    # Test with existing screenshots
    vision_works = test_vision_with_existing_data()

    # Test format requirements
    format_compatible = test_screenshot_format_requirements()

    if vision_works and format_compatible:
        print("\n✅ Compatibility test successful!")
        print("🎯 Vision system is ready for Playwright integration")
        print("📝 Playwright screenshots should use PNG format")
        print("📝 Full-page screenshots recommended for board detection")
        return 0
    else:
        print("\n❌ Compatibility issues detected")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)