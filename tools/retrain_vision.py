#!/usr/bin/env python3
"""
Retrain Vision System for 2048game.com
Quick retraining with new labeled screenshots from the current site.
"""

import sys
from pathlib import Path
import cv2
import numpy as np
import json
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from core.improved_vision import ImprovedBoardVision

def analyze_new_screenshots():
    """Analyze the new screenshots and extract color profiles"""
    print("🎯 Retraining Vision System for 2048game.com")
    print("=" * 50)

    # Screenshot data you provided
    screenshots = [
        {
            "file": "/home/nomad/Downloads/Screenshot 2025-09-18 at 16-46-59 2048 Game - Play 2048 Game Online.png",
            "board": [
                [8, 2, 8, 2],
                [2, 0, 128, 4],  # B2 is empty
                [2, 0, 16, 2],   # C2 is empty
                [4, 2, 4, 2]
            ]
        },
        {
            "file": "/home/nomad/Downloads/Screenshot 2025-09-18 at 16-46-13 2048 Game - Play 2048 Game Online.png",
            "board": [
                [0, 4, 2, 16],   # A1 is empty
                [2, 4, 32, 2],
                [2, 2, 4, 2],
                [0, 64, 2, 4]    # D1 is empty
            ]
        }
    ]

    vision = ImprovedBoardVision()
    tile_samples = {}

    for i, screenshot_data in enumerate(screenshots):
        print(f"\n📸 Processing screenshot {i+1}...")

        file_path = screenshot_data["file"]
        expected_board = np.array(screenshot_data["board"])

        # Check if file exists
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            continue

        # Load image
        image = cv2.imread(file_path)
        if image is None:
            print(f"❌ Could not load: {file_path}")
            continue

        print(f"✅ Loaded: {Path(file_path).name}")
        print(f"📏 Image size: {image.shape}")

        # Detect board region
        board_region = vision.detect_board_region(image)
        if not board_region:
            print("❌ Board region not detected")
            continue

        print(f"✅ Board region: {board_region}")

        # Extract tiles and analyze colors
        x, y, w, h = board_region
        board_img = image[y:y+h, x:x+w]

        # Extract each tile
        tile_h, tile_w = h // 4, w // 4

        for row in range(4):
            for col in range(4):
                expected_value = expected_board[row, col]

                # Extract tile region
                ty1 = row * tile_h
                ty2 = (row + 1) * tile_h
                tx1 = col * tile_w
                tx2 = (col + 1) * tile_w

                tile_img = board_img[ty1:ty2, tx1:tx2]

                # Analyze tile colors
                mean_bgr = np.mean(tile_img.reshape(-1, 3), axis=0)
                mean_rgb = [mean_bgr[2], mean_bgr[1], mean_bgr[0]]  # Convert BGR to RGB

                # Convert to HSV
                hsv_img = cv2.cvtColor(tile_img, cv2.COLOR_BGR2HSV)
                mean_hsv = np.mean(hsv_img.reshape(-1, 3), axis=0)

                # Convert to grayscale
                gray_img = cv2.cvtColor(tile_img, cv2.COLOR_BGR2GRAY)
                mean_gray = np.mean(gray_img)
                std_gray = np.std(gray_img)

                # Store sample
                if expected_value not in tile_samples:
                    tile_samples[expected_value] = []

                tile_samples[expected_value].append({
                    'mean_rgb': list(mean_rgb),
                    'mean_hsv': list(mean_hsv),
                    'mean_gray': float(mean_gray),
                    'std_gray': float(std_gray),
                    'position': f"{chr(65+row)}{col+1}",
                    'screenshot': i+1
                })

                print(f"   {chr(65+row)}{col+1}: Value={expected_value}, RGB={mean_rgb}")

    # Calculate average color profiles
    print(f"\n🧠 Calculating new color profiles...")
    new_profiles = {}

    for value, samples in tile_samples.items():
        if len(samples) == 0:
            continue

        # Average all samples for this value
        avg_rgb = np.mean([s['mean_rgb'] for s in samples], axis=0)
        avg_hsv = np.mean([s['mean_hsv'] for s in samples], axis=0)
        avg_gray = np.mean([s['mean_gray'] for s in samples])
        avg_std = np.mean([s['std_gray'] for s in samples])

        new_profiles[int(value)] = {
            'mean_rgb': avg_rgb.tolist(),
            'mean_gray': float(avg_gray),
            'uniformity': float(avg_std),
            'hsv_hue': float(avg_hsv[0]),
            'hsv_sat': float(avg_hsv[1]),
            'sample_count': len(samples)
        }

        print(f"   Value {value}: {len(samples)} samples, RGB={avg_rgb}")

    return new_profiles

def update_vision_system(new_profiles):
    """Update the vision system with new color profiles"""
    print(f"\n🔧 Updating vision system...")

    # Read current vision file
    vision_file = Path("core/improved_vision.py")
    content = vision_file.read_text()

    # Generate new profiles code
    profiles_code = "        profiles = {\n"
    for value, profile in sorted(new_profiles.items()):
        profiles_code += f"            {value}: {{  # Tile value {value} (2048game.com)\n"
        profiles_code += f"                'mean_rgb': {profile['mean_rgb']},\n"
        profiles_code += f"                'mean_gray': {profile['mean_gray']},\n"
        profiles_code += f"                'uniformity': {profile['uniformity']},\n"
        profiles_code += f"                'hsv_hue': {profile['hsv_hue']},\n"
        profiles_code += f"                'hsv_sat': {profile['hsv_sat']}\n"
        profiles_code += f"            }},\n"
    profiles_code += "        }"

    # Find and replace the profiles section
    start_marker = "        profiles = {"
    end_marker = "        }"

    start_idx = content.find(start_marker)
    if start_idx == -1:
        print("❌ Could not find profiles section")
        return False

    # Find the matching closing brace
    brace_count = 0
    end_idx = start_idx
    for i, char in enumerate(content[start_idx:], start_idx):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break

    # Replace the profiles section
    new_content = content[:start_idx] + profiles_code + content[end_idx:]

    # Write back to file
    vision_file.write_text(new_content)
    print(f"✅ Updated {vision_file}")

    return True

def test_updated_vision():
    """Test the updated vision system"""
    print(f"\n🧪 Testing updated vision system...")

    # Reload the vision system
    import importlib
    import core.improved_vision
    importlib.reload(core.improved_vision)
    from core.improved_vision import ImprovedBoardVision

    vision = ImprovedBoardVision()

    # Test with our screenshots
    test_files = [
        "/home/nomad/Downloads/Screenshot 2025-09-18 at 16-46-59 2048 Game - Play 2048 Game Online.png",
        "/home/nomad/Downloads/Screenshot 2025-09-18 at 16-46-13 2048 Game - Play 2048 Game Online.png"
    ]

    for file_path in test_files:
        if not Path(file_path).exists():
            continue

        print(f"\n📸 Testing: {Path(file_path).name}")

        image = cv2.imread(file_path)
        result = vision.analyze_board(image)

        if result['success']:
            print(f"✅ Analysis successful!")
            board = result['board_state']
            print("🎯 Detected board:")
            for i, row in enumerate(board):
                print(f"   Row {i+1}: {row}")
        else:
            print(f"❌ Analysis failed")

def main():
    """Main retraining function"""
    print("🚀 Quick Vision Retraining for 2048game.com")

    # Step 1: Analyze new screenshots
    new_profiles = analyze_new_screenshots()

    if not new_profiles:
        print("❌ No profiles generated")
        return False

    print(f"\n📊 Generated profiles for tile values: {list(new_profiles.keys())}")

    # Step 2: Update vision system
    if not update_vision_system(new_profiles):
        print("❌ Failed to update vision system")
        return False

    # Step 3: Test updated system
    test_updated_vision()

    print(f"\n🎉 Vision system retrained!")
    print(f"✅ Ready for 2048game.com automation")

    return True

if __name__ == "__main__":
    main()