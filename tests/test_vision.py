"""
Real-World Vision System Tests
All tests use REAL captured screenshots - NO SIMULATIONS

These tests require manual verification of vision accuracy.
"""

import pytest
import numpy as np
from pathlib import Path
import sys
import cv2

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.vision import BoardVision

class TestBoardVisionRealWorld:
    """Test vision system with real screenshots"""

    def setup_method(self):
        """Setup for each test"""
        self.vision = BoardVision()
        self.validation_dir = project_root / "validation_data"
        self.debug_dir = project_root / "validation_data" / "debug_vision"
        self.debug_dir.mkdir(parents=True, exist_ok=True)

        if not self.validation_dir.exists():
            pytest.skip("No validation_data directory present; capture real screenshots before running vision tests.")

        screenshots = [p for p in self.validation_dir.glob("**/*.png") if "debug" not in str(p)]
        if not screenshots:
            pytest.skip("No real screenshots found. Run easy_capture.py to generate validation images.")

        self.available_screenshots = screenshots

    def test_board_detection_real_screenshot(self):
        """Test board detection on real captured screenshot - NO SIMULATION"""
        print("\n🎯 Testing Real Board Detection")
        print("=" * 35)

        screenshots = self.available_screenshots

        # Test on most recent screenshot
        test_image_path = max(screenshots, key=lambda p: p.stat().st_mtime)
        print(f"📁 Testing: {test_image_path.name}")

        # Load real image
        image_bgr = cv2.imread(str(test_image_path))
        assert image_bgr is not None, f"Could not load {test_image_path}"

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        height, width = image_rgb.shape[:2]

        print(f"✅ Image loaded: {width}x{height}")

        # Test board detection
        board_region = self.vision.detect_board_region(image_rgb)

        # Validation
        assert board_region is not None, "Board region should be detected in real screenshot"

        x, y, w, h = board_region
        print(f"✅ Board detected: ({x}, {y}) size {w}x{h}")

        # Validate region is reasonable
        assert w > 200, f"Board width too small: {w}"
        assert h > 200, f"Board height too small: {h}"
        assert 0.7 <= w/h <= 1.3, f"Board aspect ratio unusual: {w/h}"

        # Validate region is within image bounds
        assert 0 <= x < width, f"Board x out of bounds: {x}"
        assert 0 <= y < height, f"Board y out of bounds: {y}"
        assert x + w <= width, f"Board extends beyond image width"
        assert y + h <= height, f"Board extends beyond image height"

        print("\n📋 MANUAL VERIFICATION REQUIRED:")
        print(f"   1. Check debug images in: {self.debug_dir}")
        print(f"   2. Verify detected board region is accurate")
        print(f"   3. Confirm board boundaries align with actual game board")

    def test_board_extraction_real(self):
        """Test board image extraction from real screenshot"""
        print("\n✂️  Testing Real Board Extraction")
        print("=" * 35)

        # Load real screenshot
        screenshots = self.available_screenshots
        test_image_path = max(screenshots, key=lambda p: p.stat().st_mtime)

        image_bgr = cv2.imread(str(test_image_path))
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        # Extract board
        board_image = self.vision.extract_board_image(image_rgb)

        assert board_image is not None, "Board extraction should succeed"

        height, width = board_image.shape[:2]
        print(f"✅ Board extracted: {width}x{height}")

        # Validate extracted board
        assert width >= 200, f"Extracted board too small: {width}"
        assert height >= 200, f"Extracted board too small: {height}"

        # Check that board image has content (not all black/white)
        mean_value = np.mean(board_image)
        assert 20 < mean_value < 235, f"Board image appears invalid: mean={mean_value}"

        print("\n📋 MANUAL VERIFICATION REQUIRED:")
        print(f"   1. Check debug_board_*.png in: {self.debug_dir}")
        print(f"   2. Verify extracted image contains only the game board")
        print(f"   3. Confirm no browser UI or background visible")

    def test_grid_detection_real(self):
        """Test 4x4 grid detection on real board"""
        print("\n📏 Testing Real Grid Detection")
        print("=" * 32)

        # Get real board image
        screenshots = self.available_screenshots
        test_image_path = max(screenshots, key=lambda p: p.stat().st_mtime)
        image_bgr = cv2.imread(str(test_image_path))
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        board_image = self.vision.extract_board_image(image_rgb)
        assert board_image is not None, "Need valid board image"

        # Test grid detection
        grid = self.vision.detect_grid_structure(board_image)

        assert grid is not None, "Grid detection should succeed"
        assert len(grid) == 4, f"Should have 4 rows, got {len(grid)}"

        for row_idx, row in enumerate(grid):
            assert len(row) == 4, f"Row {row_idx} should have 4 columns, got {len(row)}"

            for col_idx, (x, y, w, h) in enumerate(row):
                assert w > 0, f"Tile [{row_idx}][{col_idx}] width invalid: {w}"
                assert h > 0, f"Tile [{row_idx}][{col_idx}] height invalid: {h}"

        print(f"✅ Grid detected: 4x4 structure")
        print(f"   Sample tile sizes:")

        for row in range(min(2, len(grid))):
            for col in range(min(2, len(grid[0]))):
                x, y, w, h = grid[row][col]
                print(f"   [{row}][{col}]: {w}x{h}")

        print("\n📋 MANUAL VERIFICATION REQUIRED:")
        print(f"   1. Check debug_grid_*.png in: {self.debug_dir}")
        print(f"   2. Verify grid lines align with actual tile boundaries")
        print(f"   3. Confirm 4x4 grid division is accurate")

    def test_complete_analysis_real(self):
        """Test complete board analysis on real screenshot"""
        print("\n🎮 Testing Complete Real Board Analysis")
        print("=" * 42)

        # Load real screenshot
        screenshots = self.available_screenshots
        test_image_path = max(screenshots, key=lambda p: p.stat().st_mtime)
        image_bgr = cv2.imread(str(test_image_path))
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        print(f"📁 Analyzing: {test_image_path.name}")

        # Run complete analysis
        results = self.vision.analyze_board(image_rgb, save_debug=True)

        # Validate results structure
        assert isinstance(results, dict), "Results should be a dictionary"
        assert 'success' in results, "Results should have success flag"
        assert 'board_state' in results, "Results should have board state"
        assert 'confidence_scores' in results, "Results should have confidence scores"

        # Check board state structure
        board = results['board_state']
        assert len(board) == 4, f"Board should have 4 rows, got {len(board)}"

        for row in board:
            assert len(row) == 4, f"Each row should have 4 columns"

        # Check confidence scores structure
        confidence = results['confidence_scores']
        assert len(confidence) == 4, "Confidence should have 4 rows"

        for row in confidence:
            assert len(row) == 4, "Each confidence row should have 4 columns"
            for score in row:
                assert 0.0 <= score <= 1.0, f"Confidence score out of range: {score}"

        print(f"✅ Analysis completed:")
        print(f"   Success: {results['success']}")
        print(f"   Board detected: {results['board_detected']}")
        print(f"   Grid extracted: {results['grid_extracted']}")

        if results['board_region']:
            x, y, w, h = results['board_region']
            print(f"   Board region: ({x}, {y}) {w}x{h}")

        # Count detected tiles
        board = results['board_state']
        non_empty = sum(1 for row in board for tile in row if tile > 0)
        print(f"   Non-empty tiles detected: {non_empty}/16")

        print("\n📋 MANUAL VERIFICATION REQUIRED:")
        print(f"   1. Compare detected board state with actual game:")

        # Print detected board
        print("   📋 Detected:")
        print("      ┌─────┬─────┬─────┬─────┐")
        for row in range(4):
            row_str = "      │"
            for col in range(4):
                value = board[row][col]
                if value == 0:
                    cell = "     "
                else:
                    cell = f"{value:^5}"
                row_str += cell + "│"
            print(row_str)
            if row < 3:
                print("      ├─────┼─────┼─────┼─────┤")
        print("      └─────┴─────┴─────┴─────┘")

        print(f"\n   2. Verify this matches the actual game state")
        print(f"   3. Check debug images for accuracy assessment")
        print(f"   4. Note any incorrectly detected tiles")

        # Success criteria
        assert results['success'], "Analysis should complete successfully"

def manual_vision_test_runner():
    """
    Run manual vision tests that require human verification
    """
    print("🔍 Real-World Vision System Tests")
    print("=" * 45)
    print("These tests analyze real screenshots and require manual verification.")
    print("Ensure you have captured screenshots with easy_capture.py first.\n")

    test_instance = TestBoardVisionRealWorld()
    test_instance.setup_method()

    try:
        print("Running Board Detection Test...")
        test_instance.test_board_detection_real_screenshot()

        print("\nRunning Board Extraction Test...")
        test_instance.test_board_extraction_real()

        print("\nRunning Grid Detection Test...")
        test_instance.test_grid_detection_real()

        print("\nRunning Complete Analysis Test...")
        test_instance.test_complete_analysis_real()

        print("\n🎉 All vision tests completed!")
        print("Review all manual verification steps above.")
        print("Check debug images to assess accuracy.")

    except Exception as e:
        print(f"\n💥 Test failed: {e}")
        import traceback
        traceback.print_exc()
    except KeyboardInterrupt:
        print("\n👋 Tests cancelled by user")

if __name__ == "__main__":
    manual_vision_test_runner()
