#!/usr/bin/env python3
"""
Browser Visibility Test
Test different Playwright browser launch configurations
"""

import sys
import time
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from playwright.sync_api import sync_playwright

def test_basic_browser():
    """Test 1: Most basic browser with minimal config"""
    print("🔍 TEST 1: Basic Browser (minimal config)")
    print("=" * 50)

    with sync_playwright() as p:
        # Most basic launch
        browser = p.chromium.launch(
            headless=False,
        )
        print("✅ Browser launched")

        page = browser.new_page()
        print("✅ Page created")

        page.goto("https://example.com")
        print("✅ Navigated to example.com")

        print("⏳ Browser should be visible - waiting 5 seconds...")
        time.sleep(5)

        browser.close()
        print("✅ Browser closed")

def test_explicit_display():
    """Test 2: Browser with explicit display settings"""
    print("\n🔍 TEST 2: Browser with explicit display")
    print("=" * 50)

    # Set display explicitly
    os.environ['DISPLAY'] = ':0'

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1200,800',
                '--window-position=100,100'
            ]
        )
        print("✅ Browser launched with explicit display")

        page = browser.new_page()
        page.goto("https://2048game.com/")
        print("✅ Navigated to 2048 game")

        print("⏳ Browser should be visible - waiting 8 seconds...")
        time.sleep(8)

        browser.close()
        print("✅ Browser closed")

def test_no_args_browser():
    """Test 3: Browser with no custom arguments"""
    print("\n🔍 TEST 3: Browser with NO custom arguments")
    print("=" * 50)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[]  # Empty args
        )
        print("✅ Browser launched with no args")

        page = browser.new_page()
        page.goto("https://2048game.com/")
        print("✅ Navigated to 2048 game")

        print("⏳ Browser should be visible - waiting 8 seconds...")
        time.sleep(8)

        browser.close()
        print("✅ Browser closed")

def test_firefox_browser():
    """Test 4: Try Firefox instead of Chromium"""
    print("\n🔍 TEST 4: Firefox Browser")
    print("=" * 50)

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        print("✅ Firefox launched")

        page = browser.new_page()
        page.goto("https://2048game.com/")
        print("✅ Navigated to 2048 game")

        print("⏳ Firefox should be visible - waiting 8 seconds...")
        time.sleep(8)

        browser.close()
        print("✅ Firefox closed")

def main():
    """Run all browser visibility tests"""
    print("🚀 BROWSER VISIBILITY DEBUGGING")
    print("=" * 60)
    print("Testing different browser launch configurations...\n")

    print(f"Display: {os.environ.get('DISPLAY', 'Not set')}")
    print(f"Wayland: {os.environ.get('WAYLAND_DISPLAY', 'Not set')}")
    print(f"Session Type: {os.environ.get('XDG_SESSION_TYPE', 'Not set')}\n")

    try:
        test_basic_browser()
        test_explicit_display()
        test_no_args_browser()
        test_firefox_browser()

        print("\n🎉 ALL BROWSER TESTS COMPLETED")
        print("Check if any browser windows were visible during tests.")

    except Exception as e:
        print(f"\n❌ Browser test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()