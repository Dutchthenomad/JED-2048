#!/usr/bin/env python3
"""
Browser Automation Test
Tests browser controller functionality before full bot integration.

NO SIMULATIONS - tests actual browser automation capabilities.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.browser_controller import BrowserController, BrowserType, GameAction

def test_browser_basic():
    """Test basic browser functionality"""
    print("🌐 Testing Browser Controller")
    print("=" * 40)

    try:
        # Test browser startup
        print("📱 Starting Firefox browser...")
        controller = BrowserController(BrowserType.FIREFOX, headless=False)

        if not controller.start_browser():
            print("❌ Failed to start browser")
            return False

        print("✅ Browser started successfully")

        # Test navigation to a 2048 game
        game_url = "https://play2048.co/"  # Popular 2048 site
        print(f"🎮 Navigating to: {game_url}")

        if not controller.navigate_to_game(game_url):
            print("❌ Failed to navigate to game")
            controller.close_browser()
            return False

        print("✅ Navigation successful")

        # Test screenshot capability
        print("📸 Testing screenshot capture...")
        screenshot_path = project_root / "validation_data" / "browser_test_screenshot.png"
        screenshot_bytes = controller.take_screenshot(screenshot_path)

        if screenshot_bytes:
            print(f"✅ Screenshot saved: {screenshot_path.name} ({len(screenshot_bytes)} bytes)")
        else:
            print("❌ Screenshot failed")

        # Test game state detection
        print("🔍 Testing game state detection...")
        game_state = controller.check_game_state()
        print(f"   Game active: {game_state.get('game_active', False)}")
        print(f"   Game over: {game_state.get('game_over', False)}")
        print(f"   Score: {game_state.get('score', 'Unknown')}")

        # Test a few key inputs
        print("⌨️  Testing key inputs...")
        test_actions = [GameAction.UP, GameAction.RIGHT, GameAction.DOWN, GameAction.LEFT]

        for action in test_actions:
            print(f"   Sending: {action.name}")
            if controller.send_game_action(action):
                print(f"   ✅ {action.name} sent successfully")
                time.sleep(1)  # Wait between inputs
            else:
                print(f"   ❌ {action.name} failed")

        # Take final screenshot
        final_screenshot = project_root / "validation_data" / "browser_test_final.png"
        controller.take_screenshot(final_screenshot)
        print(f"📸 Final screenshot: {final_screenshot.name}")

        # Cleanup
        print("🧹 Closing browser...")
        controller.close_browser()
        print("✅ Browser closed")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_browser_context_manager():
    """Test browser with context manager"""
    print("\n🔄 Testing Context Manager")
    print("=" * 40)

    try:
        with BrowserController(BrowserType.FIREFOX, headless=False) as controller:
            print("✅ Browser started with context manager")

            # Quick test
            if controller.navigate_to_game("https://play2048.co/"):
                print("✅ Navigation successful")

                # Quick screenshot
                screenshot = controller.take_screenshot()
                if screenshot:
                    print(f"✅ Screenshot captured ({len(screenshot)} bytes)")
                else:
                    print("❌ Screenshot failed")
            else:
                print("❌ Navigation failed")

        print("✅ Context manager cleanup completed")
        return True

    except Exception as e:
        print(f"❌ Context manager test failed: {e}")
        return False

def quick_game_test():
    """Quick test of actual game interaction"""
    print("\n🎮 Quick Game Interaction Test")
    print("=" * 40)

    try:
        controller = BrowserController(BrowserType.FIREFOX, headless=False)

        if not controller.start_browser():
            print("❌ Browser startup failed")
            return False

        # Navigate to game
        if not controller.navigate_to_game("https://play2048.co/"):
            print("❌ Navigation failed")
            controller.close_browser()
            return False

        print("🎯 Starting quick game test...")

        # Wait for game to load
        time.sleep(3)

        # Check initial state
        initial_state = controller.check_game_state()
        print(f"Initial state: {initial_state}")

        # Take screenshot
        before_path = project_root / "validation_data" / "before_moves.png"
        controller.take_screenshot(before_path)

        # Make some moves
        moves = [GameAction.UP, GameAction.RIGHT, GameAction.DOWN, GameAction.LEFT, GameAction.UP]
        for i, move in enumerate(moves, 1):
            print(f"Move {i}: {move.name}")
            controller.send_game_action(move)
            time.sleep(1.5)  # Wait for animation

        # Take final screenshot
        after_path = project_root / "validation_data" / "after_moves.png"
        controller.take_screenshot(after_path)

        # Check final state
        final_state = controller.check_game_state()
        print(f"Final state: {final_state}")

        print("✅ Game interaction test completed")
        print(f"   Check screenshots: {before_path.name} and {after_path.name}")

        controller.close_browser()
        return True

    except Exception as e:
        print(f"❌ Game test failed: {e}")
        return False

def main():
    """Run all browser tests"""
    print("🚀 Browser Automation Test Suite")
    print("=" * 50)
    print("Testing browser automation before full bot integration\n")

    # Ensure validation directory exists
    validation_dir = project_root / "validation_data"
    validation_dir.mkdir(exist_ok=True)

    # Run tests
    tests = [
        ("Basic Browser Test", test_browser_basic),
        ("Context Manager Test", test_browser_context_manager),
        ("Game Interaction Test", quick_game_test)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)} tests")

    if passed == len(results):
        print("🎉 All browser tests passed! Ready for full bot integration.")
    else:
        print("⚠️  Some tests failed. Check browser setup and dependencies.")

if __name__ == "__main__":
    main()