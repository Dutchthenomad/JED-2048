"""
Game Board Capture System
Handles real-world screen capture for 2048 game board detection.

NO SIMULATIONS - all functionality uses real screen capture.
"""

import time
from datetime import datetime
from pathlib import Path
import numpy as np
import mss
import cv2
from typing import Optional, Tuple, Dict, Any

class GameCapture:
    """Real-world screen capture for 2048 game board"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.last_capture_time = 0
        self.capture_stats = {
            'total_captures': 0,
            'successful_captures': 0,
            'average_capture_time_ms': 0
        }

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load capture configuration"""
        # Default configuration - will be overridden by real calibration
        default_config = {
            'monitor_index': 0,  # Primary monitor
            'board_region': None,  # Will be auto-detected or manually set
            'capture_delay_ms': 100,  # Minimum time between captures
            'validation_enabled': True
        }

        # TODO: Load from actual config file when calibration is complete
        return default_config

    def get_monitor_info(self) -> Dict[str, Any]:
        """Get real monitor information - no simulation"""
        try:
            with mss.mss() as sct:
                monitors = sct.monitors
                return {
                    'monitor_count': len(monitors) - 1,  # First is "all monitors"
                    'primary_monitor': monitors[0],
                    'individual_monitors': monitors[1:],
                    'total_screen_area': monitors[0]
                }
        except Exception as e:
            raise RuntimeError(f"Failed to get monitor info: {e}")

    def capture_full_screen(self, save_path: Optional[str] = None) -> np.ndarray:
        """
        Capture full screen - REAL capture only
        Uses Wayland-compatible methods when needed

        Returns:
            numpy.ndarray: RGB image array of captured screen
        """
        start_time = time.time()

        # Try MSS first (works on X11)
        try:
            with mss.mss() as sct:
                # Capture primary monitor
                monitor = sct.monitors[self.config['monitor_index']]
                screenshot = sct.grab(monitor)

                # Convert to numpy array (RGB)
                img_array = np.frombuffer(screenshot.rgb, dtype=np.uint8)
                img_array = img_array.reshape((screenshot.height, screenshot.width, 3))

                # Update statistics
                capture_time = (time.time() - start_time) * 1000
                self._update_capture_stats(capture_time, success=True)

                # Save if requested
                if save_path:
                    self._save_capture(img_array, save_path)

                self.last_capture_time = time.time()
                return img_array

        except Exception as mss_error:
            # Fall back to Wayland-compatible method
            return self._capture_wayland_fallback(save_path, start_time)

    def capture_board_region(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        Capture specific board region if configured

        Returns:
            numpy.ndarray: RGB image array of game board region, or None if not configured
        """
        if not self.config.get('board_region'):
            # Board region not yet configured - capture full screen
            return self.capture_full_screen(save_path)

        try:
            region = self.config['board_region']

            with mss.mss() as sct:
                # Define capture region
                capture_area = {
                    'top': region['top'],
                    'left': region['left'],
                    'width': region['width'],
                    'height': region['height']
                }

                start_time = time.time()
                screenshot = sct.grab(capture_area)

                # Convert to numpy array
                img_array = np.frombuffer(screenshot.rgb, dtype=np.uint8)
                img_array = img_array.reshape((screenshot.height, screenshot.width, 3))

                # Update statistics
                capture_time = (time.time() - start_time) * 1000
                self._update_capture_stats(capture_time, success=True)

                # Save if requested
                if save_path:
                    self._save_capture(img_array, save_path)

                return img_array

        except Exception as e:
            self._update_capture_stats(0, success=False)
            raise RuntimeError(f"Board region capture failed: {e}")

    def validate_capture(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Validate captured image for 2048 game content
        Real-world validation - no simulation
        """
        if not self.config.get('validation_enabled'):
            return {'valid': True, 'reason': 'validation_disabled'}

        try:
            height, width = image.shape[:2]

            # Basic validation checks
            validations = {
                'has_content': np.mean(image) > 10,  # Not all black
                'sufficient_size': width >= 200 and height >= 200,
                'not_oversaturated': np.mean(image) < 240,  # Not all white
                'has_color_variation': np.std(image) > 10,  # Some variation
            }

            is_valid = all(validations.values())

            return {
                'valid': is_valid,
                'checks': validations,
                'image_stats': {
                    'width': width,
                    'height': height,
                    'mean_brightness': float(np.mean(image)),
                    'std_brightness': float(np.std(image))
                }
            }

        except Exception as e:
            return {
                'valid': False,
                'reason': f'validation_error: {e}'
            }

    def set_board_region(self, top: int, left: int, width: int, height: int) -> bool:
        """
        Set the board capture region based on real coordinates

        Args:
            top, left, width, height: Pixel coordinates for board region

        Returns:
            bool: True if region was set and validated
        """
        try:
            # Test capture with new region
            test_region = {
                'top': top,
                'left': left,
                'width': width,
                'height': height
            }

            # Temporarily set region for testing
            old_region = self.config.get('board_region')
            self.config['board_region'] = test_region

            # Test capture
            test_image = self.capture_board_region()
            validation = self.validate_capture(test_image)

            if validation['valid']:
                # Region is good, keep it
                return True
            else:
                # Restore old region
                self.config['board_region'] = old_region
                return False

        except Exception:
            # Restore old region on error
            self.config['board_region'] = old_region
            return False

    def get_capture_stats(self) -> Dict[str, Any]:
        """Get real capture performance statistics"""
        return self.capture_stats.copy()

    def _save_capture(self, image: np.ndarray, save_path: str) -> None:
        """Save captured image to file"""
        try:
            # Convert RGB to BGR for OpenCV
            bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(save_path, bgr_image)
        except Exception as e:
            raise RuntimeError(f"Failed to save capture: {e}")

    def _update_capture_stats(self, capture_time_ms: float, success: bool) -> None:
        """Update performance statistics"""
        self.capture_stats['total_captures'] += 1

        if success:
            self.capture_stats['successful_captures'] += 1

            # Update rolling average of capture time
            current_avg = self.capture_stats['average_capture_time_ms']
            successful_count = self.capture_stats['successful_captures']

            if successful_count == 1:
                self.capture_stats['average_capture_time_ms'] = capture_time_ms
            else:
                # Rolling average
                new_avg = ((current_avg * (successful_count - 1)) + capture_time_ms) / successful_count
                self.capture_stats['average_capture_time_ms'] = new_avg

    def _capture_wayland_fallback(self, save_path: Optional[str], start_time: float) -> np.ndarray:
        """
        Fallback capture method for Wayland systems
        Uses gnome-screenshot which works with Wayland
        """
        import subprocess
        import tempfile

        try:
            # Use temporary file if no save path provided
            if save_path is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                capture_path = temp_file.name
                temp_file.close()
            else:
                capture_path = save_path

            # Use gnome-screenshot
            result = subprocess.run([
                'gnome-screenshot',
                '-f', capture_path
            ], capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                raise RuntimeError(f"gnome-screenshot failed: {result.stderr}")

            # Load the captured image
            import cv2
            img_bgr = cv2.imread(capture_path)
            if img_bgr is None:
                raise RuntimeError("Failed to load captured image")

            # Convert BGR to RGB
            img_array = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

            # Update statistics
            capture_time = (time.time() - start_time) * 1000
            self._update_capture_stats(capture_time, success=True)

            # Clean up temp file if used
            if save_path is None:
                import os
                try:
                    os.unlink(capture_path)
                except:
                    pass

            self.last_capture_time = time.time()
            return img_array

        except Exception as e:
            self._update_capture_stats(0, success=False)
            raise RuntimeError(f"Wayland capture fallback failed: {e}")

    def __str__(self) -> str:
        """String representation of capture system status"""
        stats = self.capture_stats
        success_rate = 0 if stats['total_captures'] == 0 else (
            stats['successful_captures'] / stats['total_captures'] * 100
        )

        return (f"GameCapture(captures={stats['total_captures']}, "
                f"success_rate={success_rate:.1f}%, "
                f"avg_time={stats['average_capture_time_ms']:.1f}ms)")