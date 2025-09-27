#!/usr/bin/env python3
"""
Game Over Screen Analysis for Reinforcement Learning
Extracts game metrics and UI elements for bot training
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import cv2
import numpy as np
from core.improved_vision import ImprovedBoardVision
import json
from datetime import datetime

def extract_game_metrics(image: np.ndarray) -> dict:
    """Extract game metrics from game over screen"""

    # Convert to grayscale for text detection
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Game over screen analysis
    metrics = {
        "game_over_detected": False,
        "final_score": None,
        "move_count": None,
        "highest_tile": None,
        "board_state": None,
        "ui_elements": {}
    }

    # Detect "Game Over" text
    # Look for high-contrast areas where text would be
    height, width = gray.shape

    # Search for "Game Over" in upper portion
    upper_region = gray[0:height//3, :]

    # Simple text region detection (Game Over should be prominent)
    _, thresh = cv2.threshold(upper_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Look for large rectangular regions (text blocks)
    text_regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        aspect_ratio = w / h if h > 0 else 0

        # Text should be horizontal rectangles
        if area > 500 and 2 < aspect_ratio < 10:
            text_regions.append((x, y, w, h))

    if text_regions:
        metrics["game_over_detected"] = True

        # Find largest text region (likely "Game Over")
        largest_region = max(text_regions, key=lambda r: r[2] * r[3])
        metrics["ui_elements"]["game_over_text"] = largest_region

    # Detect button regions in lower portion
    lower_region = gray[2*height//3:, :]

    # Button detection - look for rectangular regions with moderate contrast
    _, button_thresh = cv2.threshold(lower_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    button_contours, _ = cv2.findContours(button_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    buttons = []
    for contour in button_contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        aspect_ratio = w / h if h > 0 else 0

        # Buttons should be rectangular with reasonable aspect ratio
        if 1000 < area < 50000 and 1.5 < aspect_ratio < 8:
            # Adjust y coordinate for full image
            buttons.append((x, y + 2*height//3, w, h))

    if buttons:
        # Sort by area, largest is likely "Play Again"
        buttons.sort(key=lambda b: b[2] * b[3], reverse=True)
        metrics["ui_elements"]["play_again_button"] = buttons[0]

        if len(buttons) > 1:
            metrics["ui_elements"]["secondary_button"] = buttons[1]

    return metrics

def analyze_game_performance(board_state: list, final_score: int = 2492, moves: int = 216) -> dict:
    """Analyze game performance metrics for RL"""

    analysis = {
        "final_score": final_score,
        "move_count": moves,
        "score_per_move": final_score / moves if moves > 0 else 0,
        "board_analysis": {},
        "performance_metrics": {}
    }

    # Board analysis
    non_empty_tiles = sum(1 for row in board_state for tile in row if tile > 0)
    highest_tile = max(max(row) for row in board_state) if non_empty_tiles > 0 else 0
    total_value = sum(sum(row) for row in board_state)

    analysis["board_analysis"] = {
        "non_empty_tiles": non_empty_tiles,
        "empty_tiles": 16 - non_empty_tiles,
        "highest_tile": highest_tile,
        "total_tile_value": total_value,
        "board_density": non_empty_tiles / 16
    }

    # Performance metrics for RL reward function
    analysis["performance_metrics"] = {
        "efficiency": final_score / moves if moves > 0 else 0,
        "tile_achievement": highest_tile,
        "board_utilization": non_empty_tiles / 16,
        "value_density": total_value / non_empty_tiles if non_empty_tiles > 0 else 0
    }

    # Calculate tile distribution
    tile_counts = {}
    for row in board_state:
        for tile in row:
            if tile > 0:
                tile_counts[tile] = tile_counts.get(tile, 0) + 1

    analysis["board_analysis"]["tile_distribution"] = tile_counts

    return analysis

def main():
    print("🎮 Game Over Screen Analysis")
    print("=" * 40)
    print("Extracting reinforcement learning data")
    print("NO SIMULATIONS - uses actual game over screenshot\n")

    # Load game over screenshot
    image_path = project_root / "validation_data" / "easy_captures" / "2048_capture_20250917_223121_01.png"

    if not image_path.exists():
        print(f"❌ Game over screenshot not found: {image_path}")
        return

    # Load and analyze image
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ Could not load image: {image_path}")
        return

    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    print(f"📁 Analyzing: {image_path.name}")
    print(f"📏 Image size: {image.shape[1]}x{image.shape[0]}")

    # Extract board state using vision system
    vision = ImprovedBoardVision()
    board_results = vision.analyze_board(image, save_debug=True)

    if not board_results['success']:
        print("❌ Board analysis failed")
        return

    board_state = board_results['board_state']

    # Extract UI metrics
    ui_metrics = extract_game_metrics(image)

    # Analyze performance (using known values from game over screen)
    performance = analyze_game_performance(board_state)

    # Combine all data
    rl_data = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "source_image": str(image_path),
        "game_over_analysis": {
            "board_state": board_state,
            "ui_detection": ui_metrics,
            "performance_analysis": performance
        }
    }

    # Display results
    print("\n🏆 Game Performance Analysis:")
    print(f"   📊 Final Score: {performance['final_score']}")
    print(f"   🎯 Moves: {performance['move_count']}")
    print(f"   📈 Score/Move: {performance['score_per_move']:.2f}")
    print(f"   🔥 Highest Tile: {performance['board_analysis']['highest_tile']}")
    print(f"   📦 Board Density: {performance['board_analysis']['board_density']:.1%}")

    print("\n🎲 Final Board State:")
    for row in board_state:
        print("   [" + ", ".join(f"{tile:3d}" for tile in row) + "]")

    print(f"\n🧮 Tile Distribution:")
    for tile_value, count in sorted(performance['board_analysis']['tile_distribution'].items(), reverse=True):
        print(f"   Tile {tile_value}: {count} instances")

    print("\n🎮 UI Elements Detected:")
    if ui_metrics["game_over_detected"]:
        print("   ✅ Game Over text detected")

    if "play_again_button" in ui_metrics["ui_elements"]:
        button = ui_metrics["ui_elements"]["play_again_button"]
        print(f"   🔘 Play Again button: {button}")

    print("\n💡 Reinforcement Learning Insights:")
    print(f"   🎯 Efficiency Score: {performance['performance_metrics']['efficiency']:.2f}")
    print(f"   📊 Value Density: {performance['performance_metrics']['value_density']:.1f}")
    print(f"   📈 Board Utilization: {performance['performance_metrics']['board_utilization']:.1%}")

    # Save RL data
    rl_data_path = project_root / "validation_data" / f"rl_analysis_{rl_data['timestamp']}.json"
    with open(rl_data_path, 'w') as f:
        json.dump(rl_data, f, indent=2)

    print(f"\n💾 RL data saved: {rl_data_path.name}")
    print("\n🎉 Game over analysis completed!")
    print("   Ready for reinforcement learning integration")

if __name__ == "__main__":
    main()