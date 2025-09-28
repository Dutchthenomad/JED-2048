#!/usr/bin/env python3
"""
First Principles Browser Debug
Test basic Playwright browser opening step by step
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_playwright_basic():
    """Test 1: Most basic Playwright browser opening"""
    print("🔍 TEST 1: Basic Playwright Import and Browser Opening")
    print("=" * 60)

    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright import successful")

        with sync_playwright() as p:
            print("✅ Playwright context created")

            # Try to launch browser
            print("🌐 Attempting to launch browser...")
            browser = p.chromium.launch(headless=False)
            print("✅ Browser launched successfully!")

            # Create page
            page = browser.new_page()
            print("✅ Page created")

            # Navigate to simple site
            print("🔗 Navigating to test site...")
            page.goto("https://example.com")
            print("✅ Navigation successful")

            # Wait to see browser
            print("⏳ Browser should be visible now - waiting 5 seconds...")
            time.sleep(5)

            # Cleanup
            browser.close()
            print("✅ Browser closed")

    except Exception as e:
        print(f"❌ Basic Playwright test failed: {e}")
        return False

    return True

def test_enhanced_bot_init():
    """Test 2: Enhanced2048Bot initialization without GUI"""
    print("\n🔍 TEST 2: Enhanced2048Bot Initialization")
    print("=" * 60)

    try:
        from enhanced_2048_bot import Enhanced2048Bot
        print("✅ Enhanced2048Bot import successful")

        # Initialize bot with debug output
        print("🤖 Creating Enhanced2048Bot...")
        bot = Enhanced2048Bot(
            headless=False,
            debug=True
        )
        print("✅ Bot created successfully")

        # Check controller
        print("🎮 Checking PlaywrightController...")
        if bot.controller:
            print("✅ Controller exists")
            print(f"   - Controller type: {type(bot.controller)}")
            print(f"   - Headless setting: {bot.controller.headless}")
        else:
            print("❌ No controller found")
            return False

        # Try to connect
        print("🌐 Attempting to connect to game...")
        success = bot.connect_to_game()

        if success:
            print("✅ Connection reported successful")

            # Check if browser is actually open
            if hasattr(bot.controller, 'browser') and bot.controller.browser:
                print("✅ Browser object exists")
            else:
                print("❌ No browser object found")

            if hasattr(bot.controller, 'page') and bot.controller.page:
                print("✅ Page object exists")
            else:
                print("❌ No page object found")

            # Wait to see browser
            print("⏳ Browser should be visible - waiting 10 seconds...")
            time.sleep(10)

            # Cleanup
            bot.cleanup()
            print("✅ Bot cleanup completed")
        else:
            print("❌ Connection failed")
            return False

    except Exception as e:
        print(f"❌ Enhanced2048Bot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def test_playwright_controller_direct():
    """Test 3: Direct PlaywrightController testing"""
    print("\n🔍 TEST 3: Direct PlaywrightController Testing")
    print("=" * 60)

    try:
        from core.playwright_controller import PlaywrightController
        print("✅ PlaywrightController import successful")

        # Create controller
        print("🎮 Creating PlaywrightController...")
        controller = PlaywrightController(
            headless=False,
            browser_type="chromium",
            block_ads=True
        )
        print("✅ Controller created")
        print(f"   - Headless: {controller.headless}")
        print(f"   - Browser type: {controller.browser_type}")

        # Try to connect
        print("🌐 Attempting direct connection...")
        success = controller.connect("https://2048game.com/")

        if success:
            print("✅ Connection successful")

            # Check internal state
            print("🔍 Checking controller state...")
            print(f"   - Playwright: {controller.playwright}")
            print(f"   - Browser: {controller.browser}")
            print(f"   - Page: {controller.page}")
            print(f"   - Connected: {controller.is_connected}")

            # Wait to see browser
            print("⏳ Browser should be visible - waiting 10 seconds...")
            time.sleep(10)

            # Cleanup
            controller.cleanup()
            print("✅ Controller cleanup completed")
        else:
            print("❌ Direct connection failed")
            return False

    except Exception as e:
        print(f"❌ PlaywrightController test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def main():
    """Run all browser debugging tests"""
    print("🚀 FIRST PRINCIPLES BROWSER DEBUGGING")
    print("=" * 60)
    print("Testing browser automation step by step...\n")

    # Test 1: Basic Playwright
    if not test_playwright_basic():
        print("\n💥 STOPPING: Basic Playwright test failed")
        return

    # Test 2: Enhanced2048Bot
    if not test_enhanced_bot_init():
        print("\n💥 STOPPING: Enhanced2048Bot test failed")
        return

    # Test 3: PlaywrightController
    if not test_playwright_controller_direct():
        print("\n💥 STOPPING: PlaywrightController test failed")
        return

    print("\n🎉 ALL TESTS PASSED!")
    print("Browser automation is working correctly.")

if __name__ == "__main__":
    main()