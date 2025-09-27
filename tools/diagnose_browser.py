#!/usr/bin/env python3
"""
Playwright Browser Diagnosis and Setup Tool
Diagnoses Playwright installation and verifies basic automation.
"""

import sys
from pathlib import Path

def check_playwright_import():
    """Check Playwright Python package import"""
    print("🔍 Checking Playwright Import")
    print("=" * 40)
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        print("✅ Playwright import OK")
        return True
    except Exception as e:
        print(f"❌ Playwright import failed: {e}")
        return False

def check_playwright_browsers():
    """Check that Playwright browsers are installed by starting chromium headful."""
    print("\n🔍 Checking Playwright Browsers")
    print("=" * 40)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('data:text/html,<h1>Playwright OK</h1>')
            content_ok = 'Playwright OK' in page.content()
            browser.close()
        if content_ok:
            print("✅ Chromium engine launches")
            return True
        else:
            print("❌ Chromium launch content check failed")
            return False
    except Exception as e:
        print(f"❌ Browser install check failed: {e}")
        return False
    print("=" * 40)

    try:
        result = subprocess.run(['geckodriver', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ GeckoDriver found: {result.stdout.strip()}")
            return True
        else:
            print("❌ GeckoDriver command failed")
            return False
    except FileNotFoundError:
        print("❌ GeckoDriver not found in PATH")
        return False
    except Exception as e:
        print(f"❌ GeckoDriver check failed: {e}")
        return False

def test_playwright_controller():
    """Test basic PlaywrightController operations."""
    print("\n🔍 Testing Playwright Controller")
    print("=" * 40)
    try:
        from core.playwright_controller import PlaywrightController
        ctl = PlaywrightController(headless=True, browser_type="chromium", block_ads=False)
        # Connect to a simple data URL to avoid network reliance
        ok = ctl.connect('data:text/html,<div class="game-container">OK</div>')
        if not ok:
            print("❌ Failed to open simple page")
            return False
        # Take screenshot and send a key
        shot = ctl.take_screenshot()
        keys_ok = ctl.send_key('ArrowUp')
        ctl.cleanup()
        if shot is not None and keys_ok:
            print("✅ Playwright controller basic operations OK")
            return True
        else:
            print("❌ Basic operations failed (screenshot or key)")
            return False
    except Exception as e:
        print(f"❌ PlaywrightController test failed: {e}")
        return False

def main():
    """Run Playwright-focused diagnosis."""
    print("🔧 Playwright Browser Diagnosis & Setup")
    print("=" * 50)
    print("Diagnosing Playwright installation and basic automation\n")

    results = {}
    results['playwright_import'] = check_playwright_import()
    results['playwright_browsers'] = check_playwright_browsers()
    results['playwright_controller'] = test_playwright_controller()

    print(f"\n📊 Diagnosis Summary")
    print("=" * 30)
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component.replace('_', ' ').title()}")

    print(f"\n🎯 Next Steps:")
    print("1. If import or browsers failed: activate venv and run 'pip install playwright' and 'playwright install'")
    print("2. Re-run this diagnosis to confirm")
    print("3. Test full controller: python core/playwright_controller.py")

if __name__ == "__main__":
    main()

def main():
    """Run complete Firefox diagnosis"""
    print("🔧 Firefox Browser Diagnosis & Setup")
    print("=" * 50)
    print("Diagnosing Firefox installation for browser automation\n")

    results = {}

    # Check Firefox installation
    results['firefox_installed'] = check_firefox_installation()

    # Check alternative installations
    results['firefox_snap'] = check_firefox_snap()
    results['firefox_flatpak'] = check_firefox_flatpak()

    # Check installation locations
    firefox_locations = check_firefox_locations()
    results['firefox_locations'] = len(firefox_locations) > 0

    # Check GeckoDriver
    results['geckodriver'] = check_geckodriver()

    # Test Selenium setup
    results['selenium'] = test_selenium_webdriver()

    # Summary
    print(f"\n📊 Diagnosis Summary")
    print("=" * 30)
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component.replace('_', ' ').title()}")

    # Recommendations
    print(f"\n💡 Recommendations")
    print("=" * 30)

    if not results['firefox_installed']:
        print("🔴 Firefox not properly installed")
        install_firefox_recommendations()
    else:
        print("🟢 Firefox installation looks good")

        # Try to create and test profile
        if results['selenium']:
            profile_path = create_firefox_profile()
            if profile_path:
                test_firefox_with_profile(profile_path)

    print(f"\n🎯 Next Steps:")
    print("1. Install Firefox if not present")
    print("2. Re-run this diagnosis to confirm")
    print("3. Test browser automation: python tools/test_browser.py")

if __name__ == "__main__":
    main()
