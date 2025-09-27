#!/usr/bin/env python3
"""
Simple Browser Test (Playwright)
Minimal test to verify Playwright-based automation works.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_basic_page():
    """Test basic Playwright functionality on a data URL"""
    print("🌐 Simple Playwright Test")
    print("=" * 30)

    try:
        from core.playwright_controller import PlaywrightController
        ctl = PlaywrightController(headless=True, browser_type="chromium", block_ads=False)
        ok = ctl.connect("data:text/html,<h1>Test Page</h1><div class='game-container'>OK</div>")
        if not ok:
            print("❌ Failed to open simple page")
            return False
        shot = ctl.take_screenshot()
        key_ok = ctl.send_key('ArrowUp')
        ctl.cleanup()
        print("✅ SUCCESS: Playwright automation working!")
        print(f"   Screenshot captured: {shot is not None}")
        print(f"   Key sent OK: {key_ok}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_2048_site():
    """Test actual 2048 game site (optional, requires network)"""
    print("\n🎮 Testing 2048 Game Site")
    print("=" * 30)

    try:
        from core.playwright_controller import PlaywrightController
        ctl = PlaywrightController(headless=True, browser_type="chromium", block_ads=True)
        if not ctl.connect("https://play2048.co/"):
            print("⚠️  Could not access 2048 site (network or site issue)")
            ctl.cleanup()
            return False
        screenshot_path = project_root / "validation_data" / "2048_site_test.png"
        ctl.take_screenshot(str(screenshot_path))
        ctl.send_key('ArrowUp')
        ctl.cleanup()
        print(f"✅ SUCCESS: 2048 site accessible!")
        print(f"   Screenshot saved: {screenshot_path}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    """Run simple browser tests"""
    print("🚀 Simple Browser Automation Test")
    print("=" * 40)

    # Test 1: Basic page
    success1 = test_basic_page()

    # Test 2: 2048 site
    success2 = test_2048_site()

    print(f"\n📊 Results:")
    print(f"   Basic Chrome: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   2048 Site: {'✅ PASS' if success2 else '❌ FAIL'}")

    if success1 and success2:
        print(f"\n🎉 Browser automation is working!")
        print(f"   Ready to test the full 2048 bot")
    else:
        print(f"\n⚠️  Browser automation needs troubleshooting")

if __name__ == "__main__":
    main()
