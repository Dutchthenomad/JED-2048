#!/usr/bin/env python3
"""
Test the fixed PlaywrightController browser visibility
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_fixed_controller():
    """Test the fixed PlaywrightController"""
    print("🔍 TESTING FIXED PLAYWRIGHT CONTROLLER")
    print("=" * 50)

    try:
        from core.playwright_controller import PlaywrightController
        print("✅ PlaywrightController imported")

        # Create controller with fixed settings
        controller = PlaywrightController(
            headless=False,
            browser_type="chromium",
            block_ads=True
        )
        print("✅ Controller created")
        print(f"   - Headless: {controller.headless}")

        # Connect to game
        print("🌐 Connecting to 2048 game...")
        success = controller.connect("https://2048game.com/")

        if success:
            print("✅ Connection successful!")
            print("🎮 Browser should now be VISIBLE!")

            # Wait to see browser
            print("⏳ Waiting 10 seconds to observe browser...")
            time.sleep(10)

            # Take a screenshot to verify
            print("📸 Taking screenshot...")
            screenshot = controller.take_screenshot("test_fixed_browser.png")

            if screenshot is not None:
                print(f"✅ Screenshot captured: {screenshot.shape}")
            else:
                print("❌ Screenshot failed")

            # Cleanup
            controller.cleanup()
            print("✅ Cleanup complete")

        else:
            print("❌ Connection failed")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_enhanced_bot():
    """Test Enhanced2048Bot with fixed controller"""
    print("\n🔍 TESTING ENHANCED2048BOT WITH FIXED CONTROLLER")
    print("=" * 60)

    try:
        from enhanced_2048_bot import Enhanced2048Bot
        print("✅ Enhanced2048Bot imported")

        # Create bot
        bot = Enhanced2048Bot(
            headless=False,
            debug=True
        )
        print("✅ Bot created")

        # Connect
        print("🌐 Connecting bot to game...")
        success = bot.connect_to_game()

        if success:
            print("✅ Bot connected successfully!")
            print("🎮 Browser should be VISIBLE with 2048 game!")

            # Wait to observe
            print("⏳ Waiting 10 seconds to observe browser...")
            time.sleep(10)

            # Cleanup
            bot.cleanup()
            print("✅ Bot cleanup complete")

        else:
            print("❌ Bot connection failed")

    except Exception as e:
        print(f"❌ Bot test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run fixed browser tests"""
    print("🚀 TESTING FIXED BROWSER VISIBILITY")
    print("=" * 60)

    # Test fixed controller
    test_fixed_controller()

    # Test enhanced bot
    test_enhanced_bot()

    print("\n🎉 TESTS COMPLETE!")
    print("Browser should have been visible during tests.")

if __name__ == "__main__":
    main()