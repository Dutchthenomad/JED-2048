#!/usr/bin/env python3
"""
Simple Key Input Test
The most basic test possible - just send one key and see if it works.
"""

import sys
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def test_simple_key():
    """Simplest possible key test"""
    print("🧪 Simple Key Test")
    print("=" * 30)

    try:
        from playwright.sync_api import sync_playwright

        print("📋 Starting browser...")
        with sync_playwright() as p:
            # Launch browser (visible)
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Simple HTML page that shows key presses
            simple_html = '''
            <html>
            <body style="font-size: 48px; text-align: center; padding: 100px;">
                <h1>Key Test</h1>
                <div id="output">Press any key...</div>
                <script>
                    document.addEventListener('keydown', function(e) {
                        document.getElementById('output').textContent = 'Key pressed: ' + e.key;
                    });
                </script>
            </body>
            </html>
            '''

            print("📋 Loading test page...")
            page.goto(f'data:text/html,{simple_html}')

            print("📋 Waiting 3 seconds for you to see the page...")
            time.sleep(3)

            print("📋 Sending 'a' key...")
            page.keyboard.press('a')

            print("📋 Waiting 2 seconds to see result...")
            time.sleep(2)

            print("📋 Sending Arrow key...")
            page.keyboard.press('ArrowUp')

            print("📋 Waiting 3 seconds to see result...")
            time.sleep(3)

            # Check if text changed
            output_text = page.locator('#output').text_content()
            print(f"📊 Page shows: '{output_text}'")

            browser.close()

            if "Key pressed:" in output_text:
                print("✅ KEY INPUT WORKING!")
                return True
            else:
                print("❌ Key input not detected")
                return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_key()
    if success:
        print("\n✅ SUCCESS: Key input is working")
    else:
        print("\n❌ FAILURE: Key input not working")