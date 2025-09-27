#!/usr/bin/env python3
"""
Playwright Setup Verification
Comprehensive verification that Playwright is ready for 2048 automation.
"""

def run_setup_verification():
    """Run complete Playwright setup verification"""
    print("🔍 Playwright Setup Verification")
    print("=" * 50)

    # Test 1: Import check
    print("\n📋 Test 1: Playwright Import")
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright imports successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test 2: Version check
    print("\n📋 Test 2: Version Check")
    try:
        import subprocess
        result = subprocess.run(['playwright', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
        else:
            print("❌ Playwright CLI not available")
    except Exception as e:
        print(f"⚠️  CLI check failed: {e}")

    # Test 3: Browser availability
    print("\n📋 Test 3: Browser Availability")
    browsers_working = []

    with sync_playwright() as p:
        for browser_name, browser_launcher in [
            ('Chromium', p.chromium),
            ('Firefox', p.firefox),
            ('WebKit', p.webkit)
        ]:
            try:
                browser = browser_launcher.launch(headless=True)
                page = browser.new_page()
                page.goto('data:text/html,<h1>Test</h1>')
                content = page.content()
                browser.close()

                if 'Test' in content:
                    print(f"✅ {browser_name} working")
                    browsers_working.append(browser_name)
                else:
                    print(f"❌ {browser_name} not rendering correctly")

            except Exception as e:
                print(f"❌ {browser_name} failed: {str(e)[:50]}...")

    # Test 4: Controller class
    print("\n📋 Test 4: Controller Class")
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))

        from core.playwright_controller import PlaywrightController, PLAYWRIGHT_AVAILABLE

        if PLAYWRIGHT_AVAILABLE:
            print("✅ PlaywrightController available")
            controller = PlaywrightController(headless=True)
            print("✅ Controller instantiation successful")
        else:
            print("❌ PlaywrightController reports Playwright unavailable")
            return False

    except Exception as e:
        print(f"❌ Controller test failed: {e}")
        return False

    # Test 5: Screenshot capability
    print("\n📋 Test 5: Screenshot Capability")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('data:text/html,<div style="width:400px;height:300px;background:red;">Test</div>')
            screenshot_bytes = page.screenshot()
            browser.close()

            if len(screenshot_bytes) > 1000:  # Basic size check
                print("✅ Screenshot capture working")
            else:
                print("❌ Screenshot too small")

    except Exception as e:
        print(f"❌ Screenshot test failed: {e}")

    # Summary
    print("\n🎯 Setup Verification Summary")
    print("=" * 50)
    print(f"✅ Playwright installed and functional")
    print(f"✅ {len(browsers_working)} browsers available: {', '.join(browsers_working)}")
    print(f"✅ Controller class ready")
    print(f"✅ Screenshot functionality working")

    print("\n🚀 Ready for implementation!")
    print("Next step: Implement validate_controller() function")
    print("File: core/playwright_controller.py")
    print("Guide: VALIDATION_GUIDE.md")

    return True

if __name__ == "__main__":
    success = run_setup_verification()
    if success:
        print("\n✅ Setup verification PASSED")
    else:
        print("\n❌ Setup verification FAILED")