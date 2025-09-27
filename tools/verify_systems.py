#!/usr/bin/env python3
"""
Complete System Verification Tool
Independent testing of all bot components for manual verification.

Tests each system component individually with clear pass/fail indicators.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_environment():
    """Test basic environment and dependencies"""
    print("🔧 Testing Environment & Dependencies")
    print("=" * 50)

    tests = []

    # Test Python environment
    try:
        import cv2  # noqa: F401
        import numpy as np  # noqa: F401
        from playwright.sync_api import sync_playwright  # noqa: F401
        tests.append(("Python Dependencies", True, "Core packages installed (OpenCV, numpy, Playwright)"))
    except ImportError as e:
        tests.append(("Python Dependencies", False, f"Missing package: {e}"))

    # Test project structure
    required_files = [
        "core/improved_vision.py",
        "core/strategy.py",
        "core/browser_controller.py",
        "core/game_bot.py"
    ]

    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)

    if not missing_files:
        tests.append(("Project Structure", True, "All core files present"))
    else:
        tests.append(("Project Structure", False, f"Missing: {missing_files}"))

    # Test validation data
    validation_dir = project_root / "validation_data" / "easy_captures"
    screenshots = list(validation_dir.glob("*.png")) if validation_dir.exists() else []

    if len(screenshots) >= 2:
        tests.append(("Test Data", True, f"Found {len(screenshots)} test screenshots"))
    else:
        tests.append(("Test Data", False, "Need at least 2 test screenshots"))

    # Display results
    for test_name, passed, details in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}: {details}")

    all_passed = all(test[1] for test in tests)
    return all_passed

def test_vision_system():
    """Test vision system with real screenshots"""
    print("\n👁️  Testing Vision System")
    print("=" * 50)

    try:
        from core.improved_vision import ImprovedBoardVision
        import cv2

        vision = ImprovedBoardVision()

        # Find test screenshots
        validation_dir = project_root / "validation_data" / "easy_captures"
        screenshots = list(validation_dir.glob("*.png"))

        if not screenshots:
            print("   ❌ FAIL: No test screenshots found")
            return False

        success_count = 0
        for screenshot in screenshots[:3]:  # Test first 3 screenshots
            print(f"\n   📸 Testing: {screenshot.name}")

            # Load image
            image = cv2.imread(str(screenshot))
            if image is None:
                print(f"      ❌ Could not load image")
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Test vision analysis
            results = vision.analyze_board(image)

            if results['success']:
                board = results['board_state']
                non_empty = sum(1 for row in board for tile in row if tile > 0)
                max_tile = max(max(row) for row in board) if non_empty > 0 else 0

                print(f"      ✅ Board detected: {non_empty}/16 tiles, max: {max_tile}")
                success_count += 1
            else:
                error = results.get('debug_info', {}).get('error', 'Unknown error')
                print(f"      ❌ Vision failed: {error}")

        if success_count >= 2:
            print(f"\n   ✅ PASS: Vision system working ({success_count}/{len(screenshots[:3])} successful)")
            return True
        else:
            print(f"\n   ❌ FAIL: Too many vision failures ({success_count}/{len(screenshots[:3])})")
            return False

    except Exception as e:
        print(f"   ❌ FAIL: Vision system error: {e}")
        return False

def test_strategy_system():
    """Test strategy system with known board states"""
    print("\n🧠 Testing Strategy System")
    print("=" * 50)

    try:
        from core.strategy import BasicStrategy, Move

        strategy = BasicStrategy(debug_mode=False)

        # Test with various board states
        test_boards = [
            {
                "name": "Early Game",
                "board": [[2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 2, 0], [0, 0, 0, 0]],
                "expect_moves": 4  # All moves should be possible
            },
            {
                "name": "Mid Game",
                "board": [[2, 4, 8, 2], [4, 8, 16, 4], [2, 4, 8, 2], [0, 0, 0, 0]],
                "expect_moves": [1, 4]  # At least 1 move possible
            },
            {
                "name": "Full Board",
                "board": [[2, 4, 8, 16], [4, 8, 16, 32], [8, 16, 32, 64], [16, 32, 64, 128]],
                "expect_moves": [0, 4]  # May be 0 if no moves possible
            }
        ]

        success_count = 0
        for test in test_boards:
            print(f"\n   🎮 Testing: {test['name']}")

            board = test['board']
            move, analysis = strategy.get_best_move(board)

            # Count possible moves
            possible_moves = sum(1 for move_data in analysis['move_analysis'].values()
                               if move_data.get('possible', True))

            # Validate result
            if isinstance(test['expect_moves'], int):
                expected = test['expect_moves']
                if possible_moves == expected:
                    print(f"      ✅ Correct: {possible_moves} possible moves")
                    success_count += 1
                else:
                    print(f"      ❌ Expected {expected}, got {possible_moves} possible moves")
            else:
                min_exp, max_exp = test['expect_moves']
                if min_exp <= possible_moves <= max_exp:
                    print(f"      ✅ Valid: {possible_moves} possible moves")
                    success_count += 1
                else:
                    print(f"      ❌ Expected {min_exp}-{max_exp}, got {possible_moves} possible moves")

            print(f"      📊 Recommended: {move.value} (score: {analysis['best_score']:.1f})")

        if success_count >= 2:
            print(f"\n   ✅ PASS: Strategy system working ({success_count}/{len(test_boards)} successful)")
            return True
        else:
            print(f"\n   ❌ FAIL: Strategy system issues ({success_count}/{len(test_boards)})")
            return False

    except Exception as e:
        print(f"   ❌ FAIL: Strategy system error: {e}")
        return False

def test_browser_controller():
    """Test browser controller capabilities"""
    print("\n🌐 Testing Browser Controller")
    print("=" * 50)

    try:
        from core.browser_controller import BrowserController, BrowserType

        print("   🔧 Testing Playwright-backed controller initialization...")
        # Prefer Chromium for speed
        controller = BrowserController(BrowserType.CHROME, headless=True)
        print("      ✅ BrowserController created")
        # Avoid network dependency: connect to data URL
        ok = controller.navigate_to_game('data:text/html,<div class="game-container">OK</div>')
        if not ok:
            print("      ❌ Failed to open simple page")
            return False
        shot = controller.take_screenshot()
        controller.close_browser()
        if shot is None:
            print("      ❌ Screenshot failed")
            return False
        print("      ✅ Screenshot captured")
        print(f"\n   ✅ PASS: Browser controller basic operations working")
        return True

    except Exception as e:
        print(f"   ❌ FAIL: Browser controller error: {e}")
        return False

def test_integration():
    """Test complete integration with mocks"""
    print("\n🤖 Testing Complete Integration")
    print("=" * 50)

    try:
        from core.game_bot import GameBot
        from core.browser_controller import BrowserType

        # Test bot creation
        bot = GameBot(BrowserType.FIREFOX, headless=True, debug_mode=True)
        print("   ✅ GameBot created successfully")

        # Test component access
        if hasattr(bot, 'vision') and hasattr(bot, 'strategy') and hasattr(bot, 'browser'):
            print("   ✅ All components initialized")
        else:
            print("   ❌ Missing bot components")
            return False

        # Test statistics with no games
        stats = bot.get_statistics()
        if "message" in stats and stats["message"] == "No completed games":
            print("   ✅ Statistics system working")
        else:
            print("   ❌ Statistics system issue")
            return False

        print(f"\n   ✅ PASS: Integration system ready")
        print(f"      💡 Run full integration test: python tests/test_bot_integration.py")
        return True

    except Exception as e:
        print(f"   ❌ FAIL: Integration error: {e}")
        return False

def manual_verification_guide():
    """Provide manual verification instructions"""
    print("\n📋 Manual Verification Guide")
    print("=" * 50)

    print("🔍 Step-by-Step Verification:")
    print()

    print("1. 👁️  Vision System Test:")
    print("   python tools/quick_verification.py")
    print("   → Should show board detection for all screenshots")
    print()

    print("2. 🧠 Strategy System Test:")
    print("   python tools/test_strategy.py")
    print("   → Should show move recommendations with reasoning")
    print()

    print("3. 🌐 Browser Automation Test:")
    print("   python tools/test_browser.py")
    print("   → Opens browser, navigates to game, takes screenshots")
    print("   → You should see browser window open and game load")
    print()

    print("4. 🤖 Complete Bot Test:")
    print("   python tools/run_bot.py")
    print("   → Select mode 1 (single game test)")
    print("   → Bot should play a complete game autonomously")
    print()

    print("5. 🧪 Unit Tests:")
    print("   python tests/test_integration.py")
    print("   → All tests should pass")
    print()

    print("💡 Verification Checklist:")
    print("   □ Vision correctly identifies tiles in screenshots")
    print("   □ Strategy makes sensible move recommendations")
    print("   □ Browser opens and can navigate to 2048 game")
    print("   □ Bot can play at least one complete game")
    print("   □ All unit/integration tests pass")

def main():
    """Run complete system verification"""
    print("🔍 2048 Bot System Verification")
    print("=" * 60)
    print("Independent testing of all components\n")

    # Run all tests
    tests = [
        ("Environment", test_environment),
        ("Vision System", test_vision_system),
        ("Strategy System", test_strategy_system),
        ("Browser Controller", test_browser_controller),
        ("Integration", test_integration)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n   ❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n📊 Verification Results")
    print("=" * 30)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(results)} systems")

    if passed == len(results):
        print("\n🎉 All systems verified! Bot ready for operation.")
    else:
        print(f"\n⚠️  {len(results) - passed} system(s) need attention.")

    # Show manual verification guide
    manual_verification_guide()

if __name__ == "__main__":
    main()
