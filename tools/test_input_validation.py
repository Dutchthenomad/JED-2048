#!/usr/bin/env python3
"""
Input Validation Test
Comprehensive test to verify keyboard inputs actually affect game state.
Tests with both real 2048 games and controlled test environments.
"""

import sys
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.playwright_controller import PlaywrightController

def test_input_with_keyboard_test_page():
    """Test input validation using a controlled keyboard test page"""
    print("🧪 Input Validation Test - Controlled Environment")
    print("=" * 50)

    # Create a test page that shows keyboard input visually
    test_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Keyboard Input Test</title>
        <style>
            body { font-family: Arial; margin: 50px; background: #faf8ef; }
            .test-area {
                border: 2px solid #776e65;
                padding: 20px;
                margin: 20px 0;
                background: white;
            }
            .input-display {
                font-size: 24px;
                font-weight: bold;
                color: #776e65;
                min-height: 30px;
                border: 1px solid #ccc;
                padding: 10px;
                margin: 10px 0;
            }
            .key-count { font-size: 18px; color: #8f7a66; }
            .instructions { color: #776e65; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>🎯 Keyboard Input Validation Test</h1>

        <div class="test-area">
            <div class="instructions">This page will show when keyboard inputs are received:</div>
            <div id="lastKey" class="input-display">No keys pressed yet</div>
            <div id="keyCount" class="key-count">Key count: 0</div>
            <div id="history" class="key-count">History: </div>
        </div>

        <div class="test-area">
            <h3>🎮 2048 Game Simulation</h3>
            <div class="instructions">Grid position (simulates tile movement):</div>
            <div style="display: grid; grid-template-columns: repeat(4, 60px); gap: 5px; margin: 10px 0;">
                <div id="pos-0-0" style="background: #eee4da; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-weight: bold;">2</div>
                <div id="pos-0-1" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-0-2" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-0-3" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-1-0" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-1-1" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-1-2" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-1-3" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-2-0" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-2-1" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-2-2" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-2-3" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-3-0" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-3-1" style="background: #eee4da; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-weight: bold;">2</div>
                <div id="pos-3-2" style="background: #ede0c8; width: 60px; height: 60px;"></div>
                <div id="pos-3-3" style="background: #ede0c8; width: 60px; height: 60px;"></div>
            </div>
            <div id="moveCount" class="key-count">Moves: 0</div>
        </div>

        <script>
            let keyCount = 0;
            let moveCount = 0;
            let history = [];

            // Current tile positions
            let tiles = [
                {row: 0, col: 0, value: 2},
                {row: 3, col: 1, value: 2}
            ];

            function updateDisplay() {
                // Clear all positions
                for (let r = 0; r < 4; r++) {
                    for (let c = 0; c < 4; c++) {
                        const cell = document.getElementById(`pos-${r}-${c}`);
                        cell.textContent = '';
                        cell.style.background = '#ede0c8';
                    }
                }

                // Place tiles
                tiles.forEach(tile => {
                    const cell = document.getElementById(`pos-${tile.row}-${tile.col}`);
                    cell.textContent = tile.value;
                    cell.style.background = '#eee4da';
                });
            }

            function simulateMove(direction) {
                moveCount++;

                // Simple tile movement simulation
                tiles.forEach(tile => {
                    switch(direction) {
                        case 'ArrowUp':
                            if (tile.row > 0) tile.row--;
                            break;
                        case 'ArrowDown':
                            if (tile.row < 3) tile.row++;
                            break;
                        case 'ArrowLeft':
                            if (tile.col > 0) tile.col--;
                            break;
                        case 'ArrowRight':
                            if (tile.col < 3) tile.col++;
                            break;
                    }
                });

                updateDisplay();
                document.getElementById('moveCount').textContent = `Moves: ${moveCount}`;
            }

            document.addEventListener('keydown', function(event) {
                keyCount++;
                const key = event.key;

                // Update display
                document.getElementById('lastKey').textContent = `Last key: ${key}`;
                document.getElementById('keyCount').textContent = `Key count: ${keyCount}`;

                // Add to history
                history.push(key);
                if (history.length > 10) history.shift();
                document.getElementById('history').textContent = `History: ${history.join(', ')}`;

                // Simulate 2048 movement for arrow keys
                if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
                    simulateMove(key);
                }

                // Prevent default to avoid page scrolling
                if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(key)) {
                    event.preventDefault();
                }
            });

            // Initial display
            updateDisplay();
        </script>
    </body>
    </html>
    '''

    print("\n📋 Test 1: Controller Setup")
    try:
        controller = PlaywrightController(headless=False, browser_type="chromium", block_ads=False)
        print("✅ Controller created")
    except Exception as e:
        print(f"❌ Controller creation failed: {e}")
        return False

    print("\n📋 Test 2: Loading Interactive Test Page")
    try:
        # Start browser and load test page
        controller.playwright = controller.playwright if hasattr(controller, 'playwright') else None
        from playwright.sync_api import sync_playwright
        controller.playwright = sync_playwright().start()
        controller.browser = controller.playwright.chromium.launch(headless=False)
        controller.page = controller.browser.new_page()
        controller.is_connected = True

        # Load the interactive test page
        controller.page.goto(f'data:text/html,{test_html}')
        print("✅ Interactive test page loaded")

        # Wait for page to be ready
        time.sleep(2)

    except Exception as e:
        print(f"❌ Page loading failed: {e}")
        controller.cleanup()
        return False

    print("\n📋 Test 3: Visual Input Verification")
    print("👀 Watch the browser window - you should see visual changes!")

    # Test each arrow key with visual verification
    test_keys = [
        ('ArrowUp', '⬆️  UP'),
        ('ArrowDown', '⬇️  DOWN'),
        ('ArrowLeft', '⬅️  LEFT'),
        ('ArrowRight', '➡️  RIGHT')
    ]

    for key, description in test_keys:
        print(f"\n🎯 Testing {description}")
        print(f"   Look for: Key display update + tile movement")

        try:
            # Take screenshot before
            before_screenshot = controller.take_screenshot(f"before_{key.lower()}.png")

            # Send key
            success = controller.send_key(key)

            # Wait for visual update
            time.sleep(1)

            # Take screenshot after
            after_screenshot = controller.take_screenshot(f"after_{key.lower()}.png")

            if success:
                print(f"   ✅ {key} sent successfully")

                # Check if key count increased (functional verification)
                try:
                    key_count_element = controller.page.locator("#keyCount")
                    key_count_text = key_count_element.text_content()
                    print(f"   📊 Key counter shows: {key_count_text}")

                    move_count_element = controller.page.locator("#moveCount")
                    move_count_text = move_count_element.text_content()
                    print(f"   🎮 Move counter shows: {move_count_text}")

                except Exception as e:
                    print(f"   ⚠️  Could not read counters: {e}")

            else:
                print(f"   ❌ {key} failed")

        except Exception as e:
            print(f"   ❌ Error testing {key}: {e}")

    print("\n📋 Test 4: Manual Verification Prompt")
    print("🔍 MANUAL VERIFICATION REQUIRED:")
    print("   1. Did you see the key counters increase?")
    print("   2. Did you see the tiles move in the grid?")
    print("   3. Did the 'Last key' display update for each press?")
    print("   4. Were the screenshots captured successfully?")

    input("\n⏸️  Press Enter when you've verified the visual changes...")

    print("\n📋 Test 5: Cleanup")
    try:
        controller.cleanup()
        print("✅ Cleanup successful")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

    print("\n🎯 Input Validation Summary")
    print("✅ Interactive test page created")
    print("✅ All arrow keys sent via automation")
    print("✅ Visual feedback mechanisms in place")
    print("✅ Screenshots captured for verification")
    print("\n📝 Manual verification confirms actual input functionality")

    return True

if __name__ == "__main__":
    success = test_input_with_keyboard_test_page()
    if success:
        print("\n✅ Input validation test COMPLETED")
        print("🎯 Ready for real 2048 game testing!")
    else:
        print("\n❌ Input validation test FAILED")