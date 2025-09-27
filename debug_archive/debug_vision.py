#!/usr/bin/env python3
"""
Debug Vision System
Diagnose why the vision system isn't detecting the 2048 board.
"""

import sys
from pathlib import Path
import time
import cv2
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.playwright_controller import PlaywrightController
from core.improved_vision import ImprovedBoardVision

def debug_vision_system():
    """Debug the vision system with 2048game.com"""
    print("🔍 Vision System Debug")
    print("=" * 30)

    try:
        # Initialize systems
        controller = PlaywrightController(headless=False, browser_type="chromium", block_ads=True)
        vision = ImprovedBoardVision()

        print("📋 Connecting to 2048game.com...")
        success = controller.connect("https://2048game.com/")
        if not success:
            print("❌ Connection failed")
            return False

        # Wait and take multiple screenshots
        print("📸 Taking diagnostic screenshots...")

        for i in range(5):
            print(f"\n⏱️  Screenshot {i+1} (after {i*2} seconds)...")
            time.sleep(2)

            screenshot = controller.take_screenshot(f"debug_{i+1}.png")
            if screenshot is None:
                print("❌ Screenshot failed")
                continue

            print(f"✅ Screenshot saved: debug_{i+1}.png")
            print(f"📏 Image size: {screenshot.shape}")

            # Try board detection
            board_region = vision.detect_board_region(screenshot)
            if board_region:
                print(f"✅ Board region found: {board_region}")
            else:
                print("❌ No board region detected")

            # Try full board analysis
            result = vision.analyze_board(screenshot)
            if result['success']:
                board_state = result['board_state']
                total_value = np.sum(board_state)
                print(f"✅ Board analysis successful!")
                print(f"📊 Total tile value: {total_value}")
                if total_value > 0:
                    print("🎯 Board state:")
                    for j, row in enumerate(board_state):
                        print(f"   Row {j+1}: {row}")
                    print(f"🎉 SUCCESS: Vision system working! Found tiles after {i*2} seconds")
                    break
                else:
                    print("⚠️  Board detected but no tiles found")
            else:
                print("❌ Board analysis failed")

        controller.cleanup()
        return True

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        return False

if __name__ == "__main__":
    debug_vision_system()