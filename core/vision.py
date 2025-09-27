"""
2048 Game Board Vision System
Detects and recognizes game board from real screenshots.

NO SIMULATIONS - all analysis uses real captured images.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import json

class BoardVision:
    """Real-world 2048 board detection and tile recognition"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.debug_mode = False
        self.last_analysis = {}

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load vision configuration"""
        default_config = {
            'board_detection': {
                'min_contour_area': 10000,
                'approx_epsilon': 0.02,
                'expected_aspect_ratio': 1.0,  # Square board
                'aspect_tolerance': 0.2
            },
            'tile_recognition': {
                'tile_size_min': 50,  # Minimum tile size in pixels
                'tile_size_max': 200,  # Maximum tile size in pixels
                'ocr_enabled': True,
                'color_analysis_enabled': True
            },
            'grid_detection': {
                'expected_grid_size': 4,  # 4x4 grid
                'grid_tolerance': 0.1
            }
        }

        # TODO: Load from actual config file when available
        return default_config

    def detect_board_region(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect 2048 game board region in real screenshot

        Args:
            image: RGB image array from real capture

        Returns:
            Tuple (x, y, width, height) of board region, or None if not found
        """
        if image is None or image.size == 0:
            return None

        # Convert to working format
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image.copy()

        # Find board boundaries using edge detection
        # Look for the distinctive grid pattern of 2048
        edges = cv2.Canny(gray, 50, 150)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by size and shape
        board_candidates = []
        min_area = self.config['board_detection']['min_contour_area']

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue

            # Approximate contour to polygon
            epsilon = self.config['board_detection']['approx_epsilon'] * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(contour)

            # Check aspect ratio (should be roughly square)
            aspect_ratio = w / h if h > 0 else 0
            expected_ratio = self.config['board_detection']['expected_aspect_ratio']
            tolerance = self.config['board_detection']['aspect_tolerance']

            if abs(aspect_ratio - expected_ratio) <= tolerance:
                board_candidates.append({
                    'contour': contour,
                    'bbox': (x, y, w, h),
                    'area': area,
                    'aspect_ratio': aspect_ratio
                })

        if not board_candidates:
            return None

        # Select best candidate (largest area with good aspect ratio)
        best_candidate = max(board_candidates, key=lambda c: c['area'])
        return best_candidate['bbox']

    def extract_board_image(self, image: np.ndarray, board_region: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Extract board region from full screenshot

        Args:
            image: Full screenshot
            board_region: Optional pre-detected region (x, y, w, h)

        Returns:
            Cropped board image or None if detection fails
        """
        if board_region is None:
            board_region = self.detect_board_region(image)

        if board_region is None:
            return None

        x, y, w, h = board_region

        # Validate region bounds
        if (x < 0 or y < 0 or x + w > image.shape[1] or y + h > image.shape[0] or w <= 0 or h <= 0):
            return None

        return image[y:y+h, x:x+w].copy()

    def detect_grid_structure(self, board_image: np.ndarray) -> Optional[List[List[Tuple[int, int, int, int]]]]:
        """
        Detect 4x4 grid structure within board image

        Args:
            board_image: Cropped board image

        Returns:
            4x4 list of tile regions (x, y, w, h) relative to board image
        """
        if board_image is None or board_image.size == 0:
            return None

        height, width = board_image.shape[:2]
        grid_size = self.config['grid_detection']['expected_grid_size']

        # Simple grid division approach
        # Divide board into 4x4 equal regions
        tile_width = width // grid_size
        tile_height = height // grid_size

        grid = []
        for row in range(grid_size):
            grid_row = []
            for col in range(grid_size):
                x = col * tile_width
                y = row * tile_height

                # Use actual tile size, handling remainder pixels
                actual_width = tile_width if col < grid_size - 1 else width - x
                actual_height = tile_height if row < grid_size - 1 else height - y

                grid_row.append((x, y, actual_width, actual_height))
            grid.append(grid_row)

        return grid

    def extract_tile_image(self, board_image: np.ndarray, tile_region: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """Extract individual tile image from board"""
        if board_image is None:
            return None

        x, y, w, h = tile_region

        # Validate bounds
        if (x < 0 or y < 0 or x + w > board_image.shape[1] or y + h > board_image.shape[0] or w <= 0 or h <= 0):
            return None

        return board_image[y:y+h, x:x+w].copy()

    def recognize_tile_value(self, tile_image: np.ndarray) -> int:
        """
        Recognize tile value from tile image
        Uses real image analysis - no simulation

        Args:
            tile_image: Individual tile image

        Returns:
            Tile value (0 for empty, 2, 4, 8, ... for numbered tiles)
        """
        if tile_image is None or tile_image.size == 0:
            return 0

        # Convert to grayscale for analysis
        if len(tile_image.shape) == 3:
            gray = cv2.cvtColor(tile_image, cv2.COLOR_RGB2GRAY)
        else:
            gray = tile_image.copy()

        # Check if tile appears empty (uniform background color)
        if self._is_empty_tile(gray):
            return 0

        # Try OCR-based recognition first
        if self.config['tile_recognition']['ocr_enabled']:
            ocr_result = self._recognize_with_ocr(tile_image)
            if ocr_result > 0:
                return ocr_result

        # Fall back to color-based analysis
        if self.config['tile_recognition']['color_analysis_enabled']:
            return self._recognize_with_color_analysis(tile_image)

        return 0

    def _is_empty_tile(self, gray_image: np.ndarray) -> bool:
        """Check if tile appears to be empty based on uniformity"""
        # Calculate standard deviation of pixel intensities
        std_dev = np.std(gray_image)

        # Empty tiles should have low variation
        return std_dev < 10

    def _recognize_with_ocr(self, tile_image: np.ndarray) -> int:
        """
        OCR-based tile recognition
        Real OCR on actual tile images
        """
        try:
            # Try to use pytesseract if available
            try:
                import pytesseract

                # Preprocess for better OCR
                if len(tile_image.shape) == 3:
                    gray = cv2.cvtColor(tile_image, cv2.COLOR_RGB2GRAY)
                else:
                    gray = tile_image.copy()

                # Enhance contrast
                enhanced = cv2.equalizeHist(gray)

                # OCR with number-only configuration
                text = pytesseract.image_to_string(
                    enhanced,
                    config='--psm 8 -c tessedit_char_whitelist=0123456789'
                ).strip()

                # Parse result
                if text.isdigit():
                    value = int(text)
                    # Validate it's a valid 2048 tile value
                    if value in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]:
                        return value

            except ImportError:
                # pytesseract not available, skip OCR
                pass

        except Exception:
            # OCR failed, fall back to other methods
            pass

        return 0

    def _recognize_with_color_analysis(self, tile_image: np.ndarray) -> int:
        """
        Color-based tile recognition
        Analyzes real tile colors to infer values
        """
        # Convert to HSV for better color analysis
        if len(tile_image.shape) == 3:
            hsv = cv2.cvtColor(tile_image, cv2.COLOR_RGB2HSV)
        else:
            # Grayscale, skip color analysis
            return 0

        # Calculate dominant color
        mean_hue = np.mean(hsv[:, :, 0])
        mean_saturation = np.mean(hsv[:, :, 1])
        mean_value = np.mean(hsv[:, :, 2])

        # Basic color-to-value mapping (will be refined with real data)
        # This is a starting point that will be improved with actual tile analysis
        if mean_saturation < 30:  # Low saturation, likely empty or 2
            if mean_value > 200:
                return 0  # Empty tile (bright background)
            else:
                return 2  # Tile with number 2

        # More sophisticated color analysis would go here
        # This is where we'll add real color mappings based on actual screenshots

        return 0  # Default to empty if can't determine

    def analyze_board(self, image: np.ndarray, save_debug: bool = False) -> Dict[str, Any]:
        """
        Complete board analysis from real screenshot

        Args:
            image: Real captured screenshot
            save_debug: Save debug images showing analysis steps

        Returns:
            Analysis results with board state and confidence scores
        """
        results = {
            'success': False,
            'board_detected': False,
            'grid_extracted': False,
            'board_state': [[0 for _ in range(4)] for _ in range(4)],
            'confidence_scores': [[0.0 for _ in range(4)] for _ in range(4)],
            'board_region': None,
            'debug_info': {}
        }

        try:
            # Step 1: Detect board region
            board_region = self.detect_board_region(image)
            if board_region is None:
                results['debug_info']['error'] = 'Board region not detected'
                return results

            results['board_detected'] = True
            results['board_region'] = board_region

            # Step 2: Extract board image
            board_image = self.extract_board_image(image, board_region)
            if board_image is None:
                results['debug_info']['error'] = 'Board extraction failed'
                return results

            # Step 3: Detect grid structure
            grid = self.detect_grid_structure(board_image)
            if grid is None:
                results['debug_info']['error'] = 'Grid detection failed'
                return results

            results['grid_extracted'] = True

            # Step 4: Recognize each tile
            for row in range(4):
                for col in range(4):
                    tile_region = grid[row][col]
                    tile_image = self.extract_tile_image(board_image, tile_region)

                    if tile_image is not None:
                        tile_value = self.recognize_tile_value(tile_image)
                        results['board_state'][row][col] = tile_value

                        # Basic confidence scoring
                        if tile_value > 0:
                            results['confidence_scores'][row][col] = 0.8  # Medium confidence
                        else:
                            results['confidence_scores'][row][col] = 0.9  # High confidence for empty

            results['success'] = True

            # Save debug images if requested
            if save_debug:
                self._save_debug_images(image, board_image, grid, results)

        except Exception as e:
            results['debug_info']['error'] = f'Analysis failed: {str(e)}'

        self.last_analysis = results
        return results

    def _save_debug_images(self, original_image: np.ndarray, board_image: np.ndarray,
                          grid: List[List[Tuple[int, int, int, int]]], results: Dict[str, Any]) -> None:
        """Save debug images showing analysis steps"""
        try:
            from datetime import datetime

            debug_dir = Path(__file__).parent.parent / "validation_data" / "debug_vision"
            debug_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save original with board region highlighted
            if results['board_region']:
                debug_original = original_image.copy()
                x, y, w, h = results['board_region']

                # Convert RGB to BGR for OpenCV
                if len(debug_original.shape) == 3:
                    debug_original = cv2.cvtColor(debug_original, cv2.COLOR_RGB2BGR)

                cv2.rectangle(debug_original, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.imwrite(str(debug_dir / f"debug_original_{timestamp}.png"), debug_original)

            # Save extracted board
            if board_image is not None:
                board_bgr = cv2.cvtColor(board_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(debug_dir / f"debug_board_{timestamp}.png"), board_bgr)

            # Save grid overlay
            if grid and board_image is not None:
                grid_debug = board_image.copy()
                if len(grid_debug.shape) == 3:
                    grid_debug = cv2.cvtColor(grid_debug, cv2.COLOR_RGB2BGR)

                for row in range(4):
                    for col in range(4):
                        x, y, w, h = grid[row][col]
                        cv2.rectangle(grid_debug, (x, y), (x + w, y + h), (255, 0, 0), 2)

                        # Add detected value as text
                        value = results['board_state'][row][col]
                        text = str(value) if value > 0 else "0"
                        cv2.putText(grid_debug, text, (x + 5, y + 25),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                cv2.imwrite(str(debug_dir / f"debug_grid_{timestamp}.png"), grid_debug)

        except Exception as e:
            print(f"Debug image saving failed: {e}")

    def get_analysis_summary(self) -> str:
        """Get human-readable summary of last analysis"""
        if not self.last_analysis:
            return "No analysis performed yet"

        results = self.last_analysis

        if not results['success']:
            error = results.get('debug_info', {}).get('error', 'Unknown error')
            return f"Analysis failed: {error}"

        # Count non-empty tiles
        board = results['board_state']
        non_empty_tiles = sum(1 for row in board for tile in row if tile > 0)
        max_tile = max(max(row) for row in board) if non_empty_tiles > 0 else 0

        summary = f"Board analysis successful:\n"
        summary += f"  - Non-empty tiles: {non_empty_tiles}/16\n"
        summary += f"  - Highest tile: {max_tile}\n"
        summary += f"  - Board detected: {results['board_detected']}\n"
        summary += f"  - Grid extracted: {results['grid_extracted']}"

        return summary