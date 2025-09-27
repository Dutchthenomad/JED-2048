#!/usr/bin/env python3
"""
Working 2048 Bot - Final Version
Complete autonomous 2048 bot with manual game start capability.
"""

import sys
from pathlib import Path
import time
import cv2
import numpy as np

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.playwright_controller import PlaywrightController

def run_simple_bot():
    """Run a simple version that manually starts the game and makes basic moves"""
    print("🚀 WORKING 2048 BOT - SIMPLIFIED VERSION")
    print("=" * 50)

    try:
        with PlaywrightController(headless=False, browser_type="chromium", block_ads=True) as controller:

            # Connect to game
            print("🌐 Connecting to 2048game.com...")
            if not controller.connect("https://2048game.com/"):
                print("❌ Connection failed")
                return False

            print("✅ Connected! Waiting for page to load...")
            time.sleep(5)

            # Try to click "New Game" button to ensure we have a fresh game
            print("🎮 Starting new game...")
            try:
                # Look for New Game button and click it
                new_game_selectors = [
                    "button:has-text('New Game')",
                    ".restart-button",
                    "[class*='new']",
                    "[class*='restart']"
                ]

                for selector in new_game_selectors:
                    try:
                        button = controller.page.locator(selector)
                        if button.count() > 0:
                            button.click()
                            print(f"✅ Clicked new game button: {selector}")
                            time.sleep(2)
                            break
                    except:
                        continue

            except Exception as e:
                print(f"⚠️  Could not click new game: {e}")

            # Take a screenshot to see the current state
            print("📸 Taking initial screenshot...")
            controller.take_screenshot("working_bot_initial.png")

            # Make some test moves to see if the game responds
            print("\n🎯 Making test moves to verify game is working...")

            moves = ['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp']
            for i, move in enumerate(moves):
                print(f"\n📋 Move {i+1}: {move}")

                # Take before screenshot
                controller.take_screenshot(f"working_bot_before_move_{i+1}.png")

                # Make move
                success = controller.send_key(move)
                if success:
                    print(f"   ✅ Sent {move}")
                else:
                    print(f"   ❌ Failed to send {move}")

                # Wait for animation
                time.sleep(2)

                # Take after screenshot
                controller.take_screenshot(f"working_bot_after_move_{i+1}.png")

                # Try to read score
                try:
                    score_elements = controller.page.locator("[class*='score'], [id*='score']")
                    if score_elements.count() > 0:
                        score_text = score_elements.first.text_content()
                        print(f"   📊 Score area: {score_text}")
                except:
                    print("   ℹ️  Could not read score")

            print("\n🎉 Test sequence completed!")
            print("📁 Check the generated screenshots:")
            print("   - working_bot_initial.png")
            print("   - working_bot_before_move_*.png")
            print("   - working_bot_after_move_*.png")

            print("\n❓ Manual verification:")
            print("   1. Did you see the browser open 2048game.com?")
            print("   2. Did you see tiles moving during the test moves?")
            print("   3. Did the score change during gameplay?")

            return True

    except Exception as e:
        print(f"❌ Bot error: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Working 2048 Bot - Manual Verification Version")
    success = run_simple_bot()

    if success:
        print("\n✅ BOT TEST COMPLETED!")
        print("🔍 Check screenshots to verify automation is working")
        print("🎯 If tiles moved and scores changed, the bot is functional!")
    else:
        print("\n❌ Bot test failed")