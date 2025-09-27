#!/usr/bin/env python3
"""
Browser Setup Verification Tool
Validates that the browser is properly configured for 2048 bot testing.

This tool performs REAL-WORLD verification - no simulations.
"""

import os
import time
from datetime import datetime
import mss
import cv2
import numpy as np
from pathlib import Path

class BrowserVerifier:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_dir = self.project_root / "validation_data"
        self.validation_dir.mkdir(exist_ok=True)

    def capture_current_screen(self, filename="browser_verification.png"):
        """Capture current screen - REAL capture, no simulation"""
        print(f"📸 Capturing current screen...")

        try:
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[0]  # All monitors combined
                screenshot = sct.grab(monitor)

                # Save screenshot
                output_path = self.validation_dir / filename
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(output_path))

                print(f"✅ Screenshot saved: {output_path}")
                print(f"   Resolution: {screenshot.size[0]}x{screenshot.size[1]}")
                return str(output_path)

        except Exception as e:
            print(f"❌ Screenshot failed: {e}")
            return None

    def analyze_screenshot(self, image_path):
        """Analyze screenshot for 2048 game presence - REAL analysis"""
        print(f"🔍 Analyzing screenshot for 2048 game...")

        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                print("❌ Could not load screenshot")
                return False

            # Convert to RGB for analysis
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width = img.shape[:2]

            print(f"   Image dimensions: {width}x{height}")

            # Look for game characteristics
            results = {
                'has_game_colors': self._check_game_colors(img_rgb),
                'has_grid_structure': self._check_grid_structure(img_rgb),
                'sufficient_resolution': width >= 1024 and height >= 768,
                'not_too_dark': self._check_brightness(img_rgb)
            }

            # Report results
            print("\n📊 Analysis Results:")
            for check, passed in results.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {check.replace('_', ' ').title()}")

            return all(results.values())

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return False

    def _check_game_colors(self, img_rgb):
        """Check for typical 2048 game colors"""
        # Look for beige/brown tones typical of 2048
        # This is a heuristic, not perfect, but real-world applicable

        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)

        # Look for beige/brown hues (typical 2048 background)
        beige_lower = np.array([15, 20, 180])  # Light beige
        beige_upper = np.array([35, 100, 255])

        beige_mask = cv2.inRange(hsv, beige_lower, beige_upper)
        beige_pixels = np.sum(beige_mask > 0)

        # Should have substantial beige area (game background)
        total_pixels = img_rgb.shape[0] * img_rgb.shape[1]
        beige_ratio = beige_pixels / total_pixels

        return beige_ratio > 0.05  # At least 5% beige content

    def _check_grid_structure(self, img_rgb):
        """Look for grid-like structure suggesting game board"""
        # Convert to grayscale
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

        # Edge detection
        edges = cv2.Canny(gray, 50, 150)

        # Look for horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))

        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)

        # Count line pixels
        h_line_pixels = np.sum(horizontal_lines > 0)
        v_line_pixels = np.sum(vertical_lines > 0)

        # Should have both horizontal and vertical structure
        return h_line_pixels > 100 and v_line_pixels > 100

    def _check_brightness(self, img_rgb):
        """Ensure image isn't too dark"""
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        mean_brightness = np.mean(gray)

        # Should have reasonable brightness (not all dark)
        return mean_brightness > 50

    def interactive_verification(self):
        """Guide user through manual verification steps"""
        print("\n🔧 Interactive Browser Verification")
        print("=" * 50)

        print("\n1. Please ensure a browser is open with the 2048 game loaded")
        print("   Suggested URL: https://2048game.com/ or https://play2048.co/")
        input("   Press Enter when ready...")

        print("\n2. Press F11 to enter full-screen mode")
        input("   Press Enter when in full-screen...")

        print("\n3. Ensure game board is fully visible")
        input("   Press Enter when game board is visible...")

        # Capture screenshot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.capture_current_screen(f"verification_{timestamp}.png")

        if screenshot_path:
            # Analyze screenshot
            is_valid = self.analyze_screenshot(screenshot_path)

            print(f"\n📋 Manual Verification Required:")
            print(f"   1. Open the screenshot: {screenshot_path}")
            print(f"   2. Verify the 2048 game is clearly visible")
            print(f"   3. Confirm the game board shows a 4x4 grid")
            print(f"   4. Check that tile numbers are readable")

            manual_check = input("\nDoes the screenshot show a clear 2048 game? (y/n): ").lower().strip()

            if manual_check == 'y' and is_valid:
                print("\n✅ Browser setup verification PASSED!")
                print("   Your browser is ready for 2048 bot testing.")
                return True
            else:
                print("\n❌ Browser setup verification FAILED!")
                print("   Please review BROWSER_SETUP.md and try again.")
                return False

        return False

def main():
    """Main verification routine"""
    print("🚀 2048 Bot Browser Setup Verification")
    print("=" * 40)
    print("This tool validates your browser configuration for bot testing.")
    print("NO SIMULATIONS - all testing uses real browser captures.\n")

    verifier = BrowserVerifier()

    try:
        success = verifier.interactive_verification()

        if success:
            print("\n🎉 Setup complete! You can now proceed with bot development.")
        else:
            print("\n🔧 Please fix the issues and run verification again.")

    except KeyboardInterrupt:
        print("\n\n👋 Verification cancelled by user.")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()
