#!/usr/bin/env python3
"""
Cross-browser compatibility test for 2048 bot
Tests Chromium, Firefox, and WebKit browser engines
"""

import sys
from pathlib import Path
import time
import copy

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.playwright_controller import PlaywrightController
from core.vision import BoardVision
from core.strategy import BasicStrategy

def test_browser_engine(browser_name: str):
    """Test 2048 bot functionality with specific browser engine"""
    print(f"\n🧪 TESTING {browser_name.upper()} BROWSER ENGINE")
    print("=" * 60)

    # Initialize systems
    controller = PlaywrightController(
        browser_type=browser_name.lower(),
        headless=False  # Visible testing as requested
    )
    vision = BoardVision()
    strategy = BasicStrategy()

    test_results = {
        'browser': browser_name,
        'connection': False,
        'screenshot': False,
        'vision_accuracy': False,
        'input_simulation': False,
        'game_moves': 0,
        'error': None
    }

    try:
        # Test 1: Browser connection
        print(f"🌐 Testing {browser_name} connection to 2048game.com...")
        if controller.connect():
            test_results['connection'] = True
            print(f"✅ {browser_name} connected successfully")
            time.sleep(2)  # Allow page to load
        else:
            print(f"❌ {browser_name} connection failed")
            return test_results

        # Test 2: Screenshot capability
        print(f"📸 Testing {browser_name} screenshot capture...")
        screenshot = controller.take_screenshot()
        if screenshot is not None:
            test_results['screenshot'] = True
            print(f"✅ {browser_name} screenshot captured successfully")
        else:
            print(f"❌ {browser_name} screenshot failed")
            return test_results

        # Test 3: Vision system compatibility
        print(f"👁️ Testing {browser_name} vision system compatibility...")
        analysis_result = vision.analyze_board(screenshot)
        if analysis_result and 'board_state' in analysis_result:
            board_state = analysis_result['board_state']
            if board_state is not None and len(board_state) == 4:
                test_results['vision_accuracy'] = True
                print(f"✅ {browser_name} vision system working")
                print(f"   Board detected: {board_state}")
            else:
                print(f"❌ {browser_name} vision system failed - invalid board")
                return test_results
        else:
            print(f"❌ {browser_name} vision system failed - no analysis result")
            return test_results

        # Test 4: Input simulation (3 moves)
        print(f"🎮 Testing {browser_name} input simulation (3 test moves)...")
        test_moves = ['ArrowUp', 'ArrowLeft', 'ArrowDown']
        moves_successful = 0

        for i, move in enumerate(test_moves):
            print(f"   Testing move {i+1}: {move}")

            # Take before screenshot
            before_screenshot = controller.take_screenshot()
            before_analysis = vision.analyze_board(before_screenshot)
            before_board = before_analysis.get('board_state') if before_analysis else None

            # Execute move
            if controller.send_key(move):
                time.sleep(1.5)  # Wait for animation

                # Take after screenshot
                after_screenshot = controller.take_screenshot()
                after_analysis = vision.analyze_board(after_screenshot)
                after_board = after_analysis.get('board_state') if after_analysis else None

                # Check if board changed
                if before_board != after_board:
                    moves_successful += 1
                    print(f"   ✅ Move {i+1} successful - board changed")
                else:
                    print(f"   ⚠️ Move {i+1} - board unchanged (may be valid)")
            else:
                print(f"   ❌ Move {i+1} failed to execute")

        test_results['game_moves'] = moves_successful
        if moves_successful >= 2:  # At least 2 out of 3 moves should work
            test_results['input_simulation'] = True
            print(f"✅ {browser_name} input simulation working ({moves_successful}/3 moves)")
        else:
            print(f"❌ {browser_name} input simulation insufficient ({moves_successful}/3 moves)")

    except Exception as e:
        print(f"❌ {browser_name} test failed with error: {e}")
        test_results['error'] = str(e)

    finally:
        controller.cleanup()
        time.sleep(2)  # Brief pause between browser tests

    return test_results

def run_comprehensive_browser_test():
    """Run cross-browser compatibility tests"""
    print("🧪 CROSS-BROWSER COMPATIBILITY TEST")
    print("=" * 60)
    print("🖥️ Testing 2048 bot with all Playwright browser engines")
    print("⏱️ This will test each browser sequentially with visible windows")
    print("")

    browsers_to_test = ['chromium', 'firefox', 'webkit']
    results = []

    for browser in browsers_to_test:
        result = test_browser_engine(browser)
        results.append(result)

        # Brief summary
        success_count = sum([
            result['connection'],
            result['screenshot'],
            result['vision_accuracy'],
            result['input_simulation']
        ])
        print(f"📊 {browser.upper()} Summary: {success_count}/4 tests passed")

        if browser != browsers_to_test[-1]:  # Not the last browser
            print(f"\n⏳ Waiting 3 seconds before testing next browser...")
            time.sleep(3)

    # Final comparison report
    print(f"\n{'='*60}")
    print("📊 CROSS-BROWSER COMPATIBILITY RESULTS")
    print("="*60)

    print(f"{'Browser':<10} {'Connect':<8} {'Screenshot':<10} {'Vision':<8} {'Input':<8} {'Moves':<6} {'Status':<10}")
    print("-" * 60)

    all_compatible = True
    for result in results:
        browser = result['browser'].capitalize()
        connect = "✅" if result['connection'] else "❌"
        screenshot = "✅" if result['screenshot'] else "❌"
        vision = "✅" if result['vision_accuracy'] else "❌"
        input_sim = "✅" if result['input_simulation'] else "❌"
        moves = f"{result['game_moves']}/3"

        success_count = sum([
            result['connection'],
            result['screenshot'],
            result['vision_accuracy'],
            result['input_simulation']
        ])

        if success_count >= 3:  # At least 3 out of 4 tests passed
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            all_compatible = False

        print(f"{browser:<10} {connect:<8} {screenshot:<10} {vision:<8} {input_sim:<8} {moves:<6} {status:<10}")

    print(f"\n🎯 COMPATIBILITY ASSESSMENT:")
    if all_compatible:
        print("✅ ALL BROWSERS COMPATIBLE - Production ready for cross-browser deployment")
        print("   Chromium, Firefox, and WebKit all support the 2048 bot functionality")
    else:
        print("⚠️ SOME COMPATIBILITY ISSUES DETECTED")
        print("   Review failed tests above for browser-specific issues")

    return results

if __name__ == "__main__":
    run_comprehensive_browser_test()