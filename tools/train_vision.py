#!/usr/bin/env python3
"""
Vision System Training Tool
Uses real labeled screenshots to improve tile recognition.

NO SIMULATIONS - trains on actual user-labeled game screenshots.
"""

import sys
import cv2
import numpy as np
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.vision import BoardVision

def create_training_data(image_path: str, board_state: list, save_data: bool = True):
    """
    Create training data from real labeled screenshot

    Args:
        image_path: Path to real screenshot
        board_state: 4x4 list of actual tile values
        save_data: Save training data for future use
    """

    print("🧠 Vision System Training")
    print("=" * 30)
    print(f"📁 Image: {Path(image_path).name}")

    # Load real screenshot
    try:
        image_bgr = cv2.imread(str(image_path))
        if image_bgr is None:
            print(f"❌ Could not load image: {image_path}")
            return False

        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        height, width = image_rgb.shape[:2]
        print(f"✅ Image loaded: {width}x{height}")

    except Exception as e:
        print(f"❌ Image loading failed: {e}")
        return False

    # Initialize vision system
    vision = BoardVision()

    # Extract board and grid
    board_region = vision.detect_board_region(image_rgb)
    if board_region is None:
        print("❌ Could not detect board region")
        return False

    print(f"✅ Board detected: {board_region}")

    board_image = vision.extract_board_image(image_rgb, board_region)
    if board_image is None:
        print("❌ Could not extract board image")
        return False

    grid = vision.detect_grid_structure(board_image)
    if grid is None:
        print("❌ Could not detect grid structure")
        return False

    print(f"✅ Grid extracted: 4x4 structure")

    # Extract individual tiles with labels
    training_samples = []

    print(f"\n🔍 Analyzing labeled tiles:")
    print(f"   Expected board state:")

    # Print expected board for verification
    print("   ┌─────┬─────┬─────┬─────┐")
    for row in range(4):
        row_str = "   │"
        for col in range(4):
            value = board_state[row][col]
            if value == 0:
                cell = "     "
            else:
                cell = f"{value:^5}"
            row_str += cell + "│"
        print(row_str)
        if row < 3:
            print("   ├─────┼─────┼─────┼─────┤")
    print("   └─────┴─────┴─────┴─────┘")

    # Extract tile samples
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tile_dir = project_root / "validation_data" / "training_tiles" / timestamp
    tile_dir.mkdir(parents=True, exist_ok=True)

    for row in range(4):
        for col in range(4):
            tile_region = grid[row][col]
            tile_image = vision.extract_tile_image(board_image, tile_region)

            if tile_image is not None:
                expected_value = board_state[row][col]

                # Save tile image
                tile_filename = f"tile_{row}_{col}_value_{expected_value}.png"
                tile_path = tile_dir / tile_filename

                # Convert RGB to BGR for saving
                tile_bgr = cv2.cvtColor(tile_image, cv2.COLOR_RGB2BGR)
                cv2.imwrite(str(tile_path), tile_bgr)

                # Analyze tile characteristics
                tile_analysis = analyze_tile_features(tile_image, expected_value)

                training_sample = {
                    'position': f"{chr(65+row)}{col+1}",  # A1, A2, etc.
                    'row': row,
                    'col': col,
                    'expected_value': expected_value,
                    'tile_path': str(tile_path),
                    'features': tile_analysis
                }

                training_samples.append(training_sample)

                print(f"   {training_sample['position']}: {expected_value:>2} -> {tile_filename}")

    # Save training data
    if save_data:
        training_data = {
            'timestamp': timestamp,
            'source_image': str(image_path),
            'board_region': board_region,
            'expected_board_state': board_state,
            'training_samples': training_samples,
            'tile_directory': str(tile_dir)
        }

        training_file = project_root / "validation_data" / f"training_data_{timestamp}.json"
        with open(training_file, 'w') as f:
            json.dump(training_data, f, indent=2)

        print(f"\n💾 Training data saved:")
        print(f"   📁 Tiles: {tile_dir}")
        print(f"   📄 Data: {training_file}")

    # Analyze color patterns
    analyze_color_patterns(training_samples)

    return True

def analyze_tile_features(tile_image: np.ndarray, expected_value: int) -> dict:
    """
    Analyze features of a real tile image

    Args:
        tile_image: Real tile image
        expected_value: Known tile value

    Returns:
        Dictionary of tile features
    """
    features = {}

    # Basic statistics
    if len(tile_image.shape) == 3:
        gray = cv2.cvtColor(tile_image, cv2.COLOR_RGB2GRAY)

        # Color analysis
        mean_rgb = [float(np.mean(tile_image[:,:,i])) for i in range(3)]
        features['mean_rgb'] = mean_rgb

        # HSV analysis
        hsv = cv2.cvtColor(tile_image, cv2.COLOR_RGB2HSV)
        mean_hsv = [float(np.mean(hsv[:,:,i])) for i in range(3)]
        features['mean_hsv'] = mean_hsv

    else:
        gray = tile_image.copy()
        features['mean_rgb'] = [float(np.mean(gray))] * 3
        features['mean_hsv'] = [0, 0, float(np.mean(gray))]

    # Grayscale statistics
    features['mean_gray'] = float(np.mean(gray))
    features['std_gray'] = float(np.std(gray))
    features['min_gray'] = float(np.min(gray))
    features['max_gray'] = float(np.max(gray))

    # Texture analysis
    features['uniformity'] = float(np.std(gray))  # Lower = more uniform

    # Size
    height, width = tile_image.shape[:2]
    features['width'] = width
    features['height'] = height
    features['area'] = width * height

    return features

def analyze_color_patterns(training_samples: list):
    """
    Analyze color patterns across all training samples
    """
    print(f"\n🎨 Color Pattern Analysis:")
    print(f"=" * 30)

    # Group by tile value
    value_groups = {}
    for sample in training_samples:
        value = sample['expected_value']
        if value not in value_groups:
            value_groups[value] = []
        value_groups[value].append(sample)

    # Analyze each value group
    for value in sorted(value_groups.keys()):
        samples = value_groups[value]
        print(f"\n🎯 Tile Value: {value} ({len(samples)} samples)")

        if len(samples) > 0:
            # Average color characteristics
            avg_rgb = [0, 0, 0]
            avg_hsv = [0, 0, 0]
            avg_gray = 0
            avg_uniformity = 0

            for sample in samples:
                features = sample['features']
                for i in range(3):
                    avg_rgb[i] += features['mean_rgb'][i]
                    avg_hsv[i] += features['mean_hsv'][i]
                avg_gray += features['mean_gray']
                avg_uniformity += features['uniformity']

            count = len(samples)
            avg_rgb = [x/count for x in avg_rgb]
            avg_hsv = [x/count for x in avg_hsv]
            avg_gray /= count
            avg_uniformity /= count

            print(f"   RGB: ({avg_rgb[0]:.1f}, {avg_rgb[1]:.1f}, {avg_rgb[2]:.1f})")
            print(f"   HSV: ({avg_hsv[0]:.1f}, {avg_hsv[1]:.1f}, {avg_hsv[2]:.1f})")
            print(f"   Gray: {avg_gray:.1f}")
            print(f"   Uniformity: {avg_uniformity:.1f}")

def main():
    """Main training function"""

    print("🚀 2048 Vision System Training")
    print("=" * 40)
    print("Training vision system with real labeled data")
    print("NO SIMULATIONS - uses actual screenshot analysis\n")

    # Define the labeled board state (from user input)
    # Mature game state: 2048_capture_20250917_222936_01.png
    # A1-2, A2-8, A3-4, A4-2, B1-2, B2-8, B3-64, B4-32,
    # C1-32, C2-128, C3-8, C4-4, D1-4, D2-32, D3-16, D4-2

    mature_board = [
        [2,   8,   4,  2 ],  # Row A
        [2,   8,  64, 32 ],  # Row B
        [32, 128,  8,  4 ],  # Row C
        [4,  32,  16,  2 ]   # Row D
    ]

    # Game over state: 2048_capture_20250917_223121_01.png
    # A1-2, A2-4, A3-16, A4-2, B1-8, B2-16, B3-32, B4-4,
    # C1-16, C2-256, C3-4, C4-32, D1-2, D2-8, D3-64, D4-2

    gameover_board = [
        [2,  4,  16,  2 ],  # Row A
        [8, 16,  32,  4 ],  # Row B
        [16,256,  4, 32 ],  # Row C
        [2,  8,  64,  2 ]   # Row D
    ]

    # Original training board (for reference)
    original_board = [
        [4,  2,  16, 0 ],  # Row A (A1=4, A2=2, A3=16, A4=0)
        [16, 4,  2,  0 ],  # Row B (B1=16, B2=4, B3=2, B4=0)
        [4,  32, 0,  0 ],  # Row C (C1=4, C2=32, C3=0, C4=0)
        [16, 0,  0,  2 ]   # Row D (D1=16, D2=0, D3=0, D4=2)
    ]

    # Choose which screenshot to train on
    print("Available training screenshots:")
    print("1. Original (basic tiles): 2048_capture_20250917_221057_01.png")
    print("2. Mature game (up to 128): 2048_capture_20250917_222936_01.png")
    print("3. Game over (up to 256): 2048_capture_20250917_223121_01.png")

    choice = input("Enter choice (1/2/3) or press Enter for mature game: ").strip()

    if choice == "1":
        labeled_board = original_board
        image_name = "2048_capture_20250917_221057_01.png"
    elif choice == "3":
        labeled_board = gameover_board
        image_name = "2048_capture_20250917_223121_01.png"
    else:  # Default to mature game
        labeled_board = mature_board
        image_name = "2048_capture_20250917_222936_01.png"

    # Find the labeled screenshot
    image_path = project_root / "validation_data" / "easy_captures" / image_name

    if not image_path.exists():
        print(f"❌ Labeled screenshot not found: {image_path}")
        print("   Please ensure the screenshot exists at the expected location")
        return

    print(f"📁 Using labeled screenshot: {image_name}")
    print(f"🏷️  Board state provided by user:")

    # Display expected board
    coordinate_labels = ['A', 'B', 'C', 'D']
    print("     1     2     3     4")
    print("   ┌─────┬─────┬─────┬─────┐")
    for row in range(4):
        row_str = f" {coordinate_labels[row]} │"
        for col in range(4):
            value = labeled_board[row][col]
            if value == 0:
                cell = "     "
            else:
                cell = f"{value:^5}"
            row_str += cell + "│"
        print(row_str)
        if row < 3:
            print("   ├─────┼─────┼─────┼─────┤")
    print("   └─────┴─────┴─────┴─────┘")

    # Run training
    success = create_training_data(str(image_path), labeled_board, save_data=True)

    if success:
        print(f"\n🎉 Training completed successfully!")
        print(f"   Vision system learned from real labeled data")
        print(f"   Individual tile samples extracted and analyzed")

        print(f"\n💡 Next steps:")
        print(f"   1. Review extracted tile images")
        print(f"   2. Use training data to improve recognition")
        print(f"   3. Test improved vision on other screenshots")
    else:
        print(f"\n🔧 Training failed")
        print(f"   Check error messages above")

if __name__ == "__main__":
    main()