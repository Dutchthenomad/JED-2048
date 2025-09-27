"""
Real-World Capture System Tests
All tests use REAL screen captures - NO SIMULATIONS

These tests require manual verification and real browser setup.
"""

import pytest
import numpy as np
import time
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.capture import GameCapture

class TestGameCaptureRealWorld:
    """Test capture system with real browser and screen"""

    def setup_method(self):
        """Setup for each test - requires real browser"""
        self.capture = GameCapture()
        self.test_output_dir = project_root / "validation_data" / "test_captures"
        self.test_output_dir.mkdir(parents=True, exist_ok=True)

    def test_monitor_detection_real(self):
        """Test real monitor detection - NO SIMULATION"""
        print("\n🖥️  Testing Real Monitor Detection")
        print("=" * 40)

        monitor_info = self.capture.get_monitor_info()

        # Validate real monitor data
        assert monitor_info['monitor_count'] >= 1, "Must have at least one monitor"
        assert 'primary_monitor' in monitor_info
        assert 'width' in monitor_info['primary_monitor']
        assert 'height' in monitor_info['primary_monitor']

        # Print real monitor info for manual verification
        print(f"✅ Monitor Count: {monitor_info['monitor_count']}")
        print(f"✅ Primary Monitor: {monitor_info['primary_monitor']['width']}x{monitor_info['primary_monitor']['height']}")

        # Manual verification required
        print("\n📋 MANUAL VERIFICATION REQUIRED:")
        print("   1. Check that monitor count matches your actual setup")
        print("   2. Verify resolution matches your primary monitor")

    def test_full_screen_capture_real(self):
        """Test real full-screen capture - NO SIMULATION"""
        print("\n📸 Testing Real Full-Screen Capture")
        print("=" * 42)

        # Inform user about test requirements
        print("🔧 SETUP REQUIRED:")
        print("   1. Ensure Firefox is open with 2048 game")
        print("   2. Game should be visible on screen")
        print("   3. Press Enter when ready for capture...")
        input()

        # Perform real capture
        timestamp = int(time.time())
        capture_path = self.test_output_dir / f"fullscreen_test_{timestamp}.png"

        start_time = time.time()
        captured_image = self.capture.capture_full_screen(str(capture_path))
        capture_time = (time.time() - start_time) * 1000

        # Validate capture results
        assert captured_image is not None, "Capture should return an image"
        assert isinstance(captured_image, np.ndarray), "Should return numpy array"
        assert len(captured_image.shape) == 3, "Should be RGB image"
        assert captured_image.shape[2] == 3, "Should have 3 color channels"

        height, width = captured_image.shape[:2]
        assert width >= 800, f"Screen width too small: {width}"
        assert height >= 600, f"Screen height too small: {height}"

        # Performance validation
        assert capture_time < 100, f"Capture too slow: {capture_time:.1f}ms"

        print(f"✅ Capture successful: {width}x{height}")
        print(f"✅ Capture time: {capture_time:.1f}ms")
        print(f"✅ Saved to: {capture_path}")

        # Manual verification required
        print("\n📋 MANUAL VERIFICATION REQUIRED:")
        print(f"   1. Open: {capture_path}")
        print("   2. Verify 2048 game is visible in screenshot")
        print("   3. Check image quality is acceptable")

        # Verify file was created and has content
        assert capture_path.exists(), "Screenshot file should exist"
        assert capture_path.stat().st_size > 10000, "Screenshot file should have reasonable size"

    def test_capture_validation_real(self):
        """Test capture validation with real images - NO SIMULATION"""
        print("\n🔍 Testing Real Capture Validation")
        print("=" * 37)

        # Capture real image for validation
        real_image = self.capture.capture_full_screen()
        validation_result = self.capture.validate_capture(real_image)

        # Check validation structure
        assert isinstance(validation_result, dict), "Should return validation dict"
        assert 'valid' in validation_result, "Should have validity flag"
        assert 'checks' in validation_result, "Should have check details"

        # Print validation results for manual review
        print(f"✅ Image Valid: {validation_result['valid']}")
        print("✅ Validation Checks:")
        for check, passed in validation_result['checks'].items():
            status = "✅" if passed else "❌"
            print(f"   {status} {check}: {passed}")

        if 'image_stats' in validation_result:
            stats = validation_result['image_stats']
            print(f"✅ Image Stats:")
            print(f"   - Size: {stats['width']}x{stats['height']}")
            print(f"   - Brightness: {stats['mean_brightness']:.1f}")
            print(f"   - Variation: {stats['std_brightness']:.1f}")

        # Manual verification
        print("\n📋 MANUAL VERIFICATION REQUIRED:")
        print("   1. Review validation results above")
        print("   2. Confirm they match your visual assessment")
        print("   3. Check if any failed validations are concerning")

    def test_performance_benchmark_real(self):
        """Benchmark real capture performance - NO SIMULATION"""
        print("\n⚡ Testing Real Capture Performance")
        print("=" * 37)

        print("🔧 This test will capture 10 screenshots rapidly")
        print("   Ensure 2048 game is visible and press Enter...")
        input()

        # Benchmark real captures
        capture_times = []
        num_captures = 10

        for i in range(num_captures):
            start_time = time.time()
            image = self.capture.capture_full_screen()
            capture_time = (time.time() - start_time) * 1000

            capture_times.append(capture_time)
            print(f"   Capture {i+1}: {capture_time:.1f}ms")

            # Small delay to avoid overwhelming the system
            time.sleep(0.1)

        # Calculate performance metrics
        avg_time = np.mean(capture_times)
        max_time = np.max(capture_times)
        min_time = np.min(capture_times)

        print(f"\n✅ Performance Results:")
        print(f"   - Average: {avg_time:.1f}ms")
        print(f"   - Maximum: {max_time:.1f}ms")
        print(f"   - Minimum: {min_time:.1f}ms")

        # Performance assertions
        assert avg_time < 50, f"Average capture time too slow: {avg_time:.1f}ms"
        assert max_time < 100, f"Maximum capture time too slow: {max_time:.1f}ms"

        # Check capture system statistics
        stats = self.capture.get_capture_stats()
        print(f"✅ System Stats: {stats}")

        print("\n📋 MANUAL VERIFICATION REQUIRED:")
        print("   1. Confirm performance meets real-time requirements")
        print("   2. Check if any captures were unusually slow")

    def test_board_region_setting_manual(self):
        """Test setting board region with manual coordinates - REAL TESTING"""
        print("\n🎯 Testing Board Region Setting")
        print("=" * 32)

        print("🔧 MANUAL COORDINATE SELECTION:")
        print("   1. Open 2048 game in browser")
        print("   2. Note the game board boundaries")
        print("   3. Estimate coordinates (or use browser dev tools)")

        # Get user input for real coordinates
        try:
            print("\nEnter board region coordinates:")
            left = int(input("   Left edge (pixels from left): "))
            top = int(input("   Top edge (pixels from top): "))
            width = int(input("   Width (pixels): "))
            height = int(input("   Height (pixels): "))

            print(f"\n📍 Testing region: left={left}, top={top}, width={width}, height={height}")

            # Test setting the region
            success = self.capture.set_board_region(top, left, width, height)

            if success:
                print("✅ Board region set successfully")

                # Test capture with new region
                timestamp = int(time.time())
                region_path = self.test_output_dir / f"board_region_test_{timestamp}.png"
                board_image = self.capture.capture_board_region(str(region_path))

                assert board_image is not None, "Board region capture should work"

                print(f"✅ Board region captured: {board_image.shape}")
                print(f"✅ Saved to: {region_path}")

                print("\n📋 MANUAL VERIFICATION REQUIRED:")
                print(f"   1. Open: {region_path}")
                print("   2. Verify it shows ONLY the game board")
                print("   3. Check that all 4x4 tiles are visible")

            else:
                print("❌ Board region setting failed")
                print("   This might be due to invalid coordinates")

        except ValueError:
            print("❌ Invalid coordinates entered")
            pytest.skip("Manual coordinate input failed")
        except KeyboardInterrupt:
            pytest.skip("Test cancelled by user")

def manual_test_runner():
    """
    Run manual tests that require human interaction
    Call this function to run real-world tests
    """
    print("🚀 Real-World Capture System Tests")
    print("=" * 50)
    print("These tests require manual setup and verification.")
    print("Ensure 2048 game is open in Firefox before starting.\n")

    test_instance = TestGameCaptureRealWorld()
    test_instance.setup_method()

    try:
        print("Running Monitor Detection Test...")
        test_instance.test_monitor_detection_real()

        print("\nRunning Full Screen Capture Test...")
        test_instance.test_full_screen_capture_real()

        print("\nRunning Capture Validation Test...")
        test_instance.test_capture_validation_real()

        print("\nRunning Performance Benchmark...")
        test_instance.test_performance_benchmark_real()

        print("\nRunning Board Region Test...")
        test_instance.test_board_region_setting_manual()

        print("\n🎉 All capture tests completed!")
        print("Review all manual verification steps above.")

    except Exception as e:
        print(f"\n💥 Test failed: {e}")
    except KeyboardInterrupt:
        print("\n👋 Tests cancelled by user")

if __name__ == "__main__":
    manual_test_runner()