#!/usr/bin/env python3
"""
Environment test script to verify display and browser functionality
"""

import sys
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.playwright_controller import PlaywrightController

def test_environment():
    """Test that we can launch a visible browser and take a screenshot"""
    print("🧪 ENVIRONMENT TEST - DISPLAY & BROWSER FUNCTIONALITY")
    print("=" * 60)

    print("🖥️  Testing display environment...")
    print(f"   Display: {os.environ.get('DISPLAY', 'Not set')}")

    print("\n🌐 Testing Playwright browser launch...")

    # Test with non-headless mode to see browser window
    controller = PlaywrightController(
        headless=False,  # Make browser visible
        browser_type="chromium",
        block_ads=True
    )

    try:
        print("   🚀 Launching browser...")
        success = controller.connect()

        if success:
            print("   ✅ Browser launched successfully!")
            print("   📱 Navigating to test page...")

            # Navigate to a simple test page
            page = controller.page
            page.goto("https://example.com")

            print("   ⏳ Waiting 3 seconds for visual confirmation...")
            time.sleep(3)

            print("   📸 Taking test screenshot...")
            screenshot = controller.take_screenshot()

            if screenshot is not None:
                print("   ✅ Screenshot capture successful!")
                print(f"   📏 Screenshot size: {screenshot.shape}")
            else:
                print("   ❌ Screenshot capture failed!")

            print("   🧹 Cleaning up...")
            controller.cleanup()
            print("   ✅ Browser closed successfully!")

        else:
            print("   ❌ Browser launch failed!")

    except Exception as e:
        print(f"   ❌ Environment test failed: {e}")
        try:
            controller.cleanup()
        except:
            pass

if __name__ == "__main__":
    import os
    test_environment()