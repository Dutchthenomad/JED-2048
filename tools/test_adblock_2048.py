#!/usr/bin/env python3
"""
Ad Blocking Test with 2048
Test that ad blocking works without breaking game functionality.
"""

import sys
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def test_with_adblock_enabled():
    """Test 2048 automation with ad blocking enabled"""
    print("🛡️  2048 Game Test - Ad Blocking Enabled")
    print("=" * 45)

    try:
        from playwright.sync_api import sync_playwright
        import cv2
        import numpy as np

        with sync_playwright() as p:
            # Launch with enhanced ad blocking
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--disable-background-networking',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-extensions',
                    '--no-first-run',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--block-new-web-contents',  # Block pop-ups
                    '--disable-popup-blocking',   # Paradoxically helps control pop-ups
                ]
            )

            page = browser.new_page()

            # Enhanced ad blocking at page level
            def enhanced_ad_blocker(route):
                """Enhanced ad blocking function"""
                url = route.request.url.lower()

                # Allow the main game domain and essential resources
                allowed_patterns = [
                    '2048game.com',
                    'github.io',
                    'play2048.co',
                    'cdnjs.cloudflare.com',
                    'fonts.googleapis.com',
                    'fonts.gstatic.com'
                ]

                # Allow if from allowed domain/pattern
                if any(pattern in url for pattern in allowed_patterns):
                    route.continue_()
                    return

                # Block known ad/tracking patterns
                blocked_patterns = [
                    'doubleclick',
                    'googlesyndication',
                    'googletagmanager',
                    'google-analytics',
                    'facebook.com/tr',
                    'googleadservices',
                    'adsystem',
                    'amazon-adsystem',
                    'scorecardresearch',
                    'outbrain',
                    'taboola',
                    'adsafeprotected',
                    'moatads',
                    'newrelic',
                    'hotjar',
                    'amplitude',
                    'mixpanel',
                    'segment',
                    '/ads/',
                    '/ad/',
                    'advertising',
                    'analytics',
                    'tracking',
                    'metrics',
                    'telemetry',
                    'popup',
                    'popunder'
                ]

                # Block if URL contains blocked patterns
                if any(pattern in url for pattern in blocked_patterns):
                    print(f"🚫 Blocked: {url[:50]}...")
                    route.abort()
                    return

                # Allow everything else
                route.continue_()

            # Set up request interception
            page.route('**/*', enhanced_ad_blocker)

            # Block additional pop-up related JavaScript
            page.add_init_script("""
                // Block common pop-up methods
                window.open = function() { return null; };
                window.showModalDialog = function() { return null; };

                // Override alert/confirm to prevent blocking
                window.alert = function() {};
                window.confirm = function() { return true; };

                // Block focus stealing
                window.focus = function() {};
                window.blur = function() {};
            """)

            print("🛡️  Enhanced ad blocking configured")

            # Load the working 2048 site
            print("📋 Loading 2048game.com with ad blocking...")
            try:
                page.goto("https://2048game.com/", timeout=20000)
                time.sleep(3)
                print("✅ Game loaded successfully")
            except Exception as e:
                print(f"❌ Failed to load: {e}")
                browser.close()
                return False

            # Check for pop-ups or overlays
            print("\n🔍 Checking for pop-ups/overlays...")
            overlay_selectors = [
                "[id*='popup']", "[class*='popup']",
                "[id*='modal']", "[class*='modal']",
                "[id*='overlay']", "[class*='overlay']",
                "[id*='ad']", "[class*='ad']",
                "[style*='z-index: 999']", "[style*='position: fixed']"
            ]

            overlays_found = 0
            for selector in overlay_selectors:
                try:
                    elements = page.locator(selector)
                    count = elements.count()
                    if count > 0:
                        overlays_found += count
                        print(f"   ⚠️  Found {count} elements matching '{selector}'")
                except:
                    pass

            if overlays_found == 0:
                print("   ✅ No obvious pop-ups/overlays detected")
            else:
                print(f"   🚫 Found {overlays_found} potential overlay elements")

            # Take initial screenshot to check cleanliness
            print("\n📸 Taking clean screenshot...")
            page.screenshot(path="game_with_adblock.png")

            # Test game interaction with ad blocking
            print("\n🎮 Testing game interaction with ad blocking...")
            initial_img = cv2.imread("game_with_adblock.png")

            moves_successful = 0
            test_moves = [
                ('ArrowRight', 'RIGHT'),
                ('ArrowDown', 'DOWN'),
                ('ArrowLeft', 'LEFT'),
                ('ArrowUp', 'UP')
            ]

            for i, (key, direction) in enumerate(test_moves):
                print(f"\n📋 Move {i+1}: {direction}")

                # Send key
                page.keyboard.press(key)
                print(f"   ✅ Sent {key}")

                # Wait for animation
                time.sleep(1.5)

                # Take screenshot after move
                after_path = f"adblock_move_{i+1}.png"
                page.screenshot(path=after_path)

                # Compare screenshots
                after_img = cv2.imread(after_path)
                if after_img is not None:
                    diff = cv2.absdiff(initial_img, after_img)
                    diff_sum = np.sum(diff)

                    print(f"   📸 Screenshot: {after_path}")
                    print(f"   🔍 Change score: {diff_sum}")

                    if diff_sum > 100000:
                        print(f"   ✅ Game responded - move successful!")
                        moves_successful += 1
                        initial_img = after_img.copy()
                    else:
                        print(f"   ⚠️  Minimal change detected")

            # Results
            print(f"\n📊 Ad Blocking Test Results:")
            print(f"   🛡️  Ad blocking: ENABLED")
            print(f"   🎯 Moves attempted: {len(test_moves)}")
            print(f"   ✅ Successful moves: {moves_successful}")
            print(f"   📈 Success rate: {moves_successful/len(test_moves)*100:.1f}%")
            print(f"   🚫 Overlay elements: {overlays_found}")

            browser.close()

            # Determine success
            if moves_successful >= 3 and overlays_found < 5:
                print("\n🎉 SUCCESS: Ad blocking works without breaking game!")
                print("✅ Game functionality preserved")
                print("✅ Pop-ups/ads blocked")
                return True
            else:
                print("\n⚠️  Mixed results - may need ad blocking adjustments")
                return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_comparison_without_adblock():
    """Quick test without ad blocking to compare"""
    print("\n🔍 Comparison Test - No Ad Blocking")
    print("=" * 40)

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            print("📋 Loading 2048game.com WITHOUT ad blocking...")
            page.goto("https://2048game.com/", timeout=15000)
            time.sleep(5)  # Extra time for ads to load

            # Count potential ad elements
            ad_selectors = [
                "[id*='ad']", "[class*='ad']",
                "[id*='popup']", "[class*='popup']",
                "iframe", "[src*='doubleclick']"
            ]

            ad_elements = 0
            for selector in ad_selectors:
                try:
                    count = page.locator(selector).count()
                    ad_elements += count
                    if count > 0:
                        print(f"   📊 {count} elements: {selector}")
                except:
                    pass

            print(f"📊 Without ad blocking: {ad_elements} potential ad elements found")

            page.screenshot(path="game_no_adblock.png")
            browser.close()

            return ad_elements

    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        return 999  # High number indicates failure

def main():
    """Main test function"""
    print("🚀 Ad Blocking Integration Test")
    print("Testing that ad blocking doesn't break 2048 automation")

    # Test with ad blocking
    adblock_success = test_with_adblock_enabled()

    # Quick comparison without ad blocking
    ad_count_without_blocking = test_comparison_without_adblock()

    print(f"\n📊 Final Comparison:")
    print(f"   🛡️  With ad blocking: {'SUCCESS' if adblock_success else 'ISSUES'}")
    print(f"   📈 Without ad blocking: {ad_count_without_blocking} ad elements")

    if adblock_success:
        print("\n🎉 AD BLOCKING INTEGRATION SUCCESSFUL!")
        print("✅ Game works with ad blocking")
        print("✅ Automation preserved")
        print("✅ Ads blocked effectively")
        print("\n🚀 Ready for full bot deployment!")
    else:
        print("\n🔧 Ad blocking needs adjustment")

if __name__ == "__main__":
    main()