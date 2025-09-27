#!/usr/bin/env python3
"""
Quick weight comparison test - shorter games to compare configurations efficiently
"""

import sys
from pathlib import Path
import copy
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from complete_2048_bot import Complete2048Bot

def quick_weight_comparison():
    """Compare key weight configurations with shorter games"""
    print("⚡ QUICK WEIGHT COMPARISON TEST")
    print("=" * 50)
    print("🖥️  Visible gameplay - shorter tests for efficiency")
    print("")

    # Define focused weight configurations
    configurations = {
        "baseline": {
            'empty_tiles': 100.0,
            'merge_potential': 50.0,
            'corner_bonus': 200.0,
            'monotonicity': 30.0,
            'max_tile_value': 10.0
        },

        "optimized": {
            'empty_tiles': 150.0,      # +50% empty space focus
            'merge_potential': 100.0,  # Double merge priority
            'corner_bonus': 250.0,     # +25% corner strategy
            'monotonicity': 75.0,      # +150% monotonicity
            'max_tile_value': 15.0     # +50% tile value
        }
    }

    results = []

    for config_name, weights in configurations.items():
        print(f"\n🎯 Testing {config_name.upper()} configuration...")
        print(f"Weights: {weights}")

        # Create bot
        bot = Complete2048Bot(headless=False, debug=True)

        try:
            # Set weights
            bot.strategy.weights = copy.deepcopy(weights)

            # Connect and play short game
            if bot.connect_to_game():
                print(f"🚀 Starting {config_name} game (max 25 moves)...")
                game_results = bot.play_autonomous_game(max_moves=25)

                moves = game_results.get('moves_completed', 0)
                score = game_results.get('final_score', 0)
                tile = game_results.get('highest_tile', 0)
                efficiency = score / moves if moves > 0 else 0

                result = {
                    'config': config_name,
                    'moves': moves,
                    'score': score,
                    'highest_tile': tile,
                    'efficiency': efficiency
                }
                results.append(result)

                print(f"✅ {config_name} results:")
                print(f"   Moves: {moves}, Score: {score}, Tile: {tile}")
                print(f"   Efficiency: {efficiency:.3f} points/move")

        except Exception as e:
            print(f"❌ {config_name} test failed: {e}")

        finally:
            bot.cleanup()
            time.sleep(2)  # Brief pause between tests

    # Comparison
    if len(results) >= 2:
        print(f"\n📊 WEIGHT COMPARISON RESULTS")
        print("=" * 40)

        baseline_eff = next((r['efficiency'] for r in results if r['config'] == 'baseline'), 0)
        optimized_eff = next((r['efficiency'] for r in results if r['config'] == 'optimized'), 0)

        print(f"Baseline efficiency:  {baseline_eff:.3f} points/move")
        print(f"Optimized efficiency: {optimized_eff:.3f} points/move")

        if optimized_eff > baseline_eff:
            improvement = optimized_eff - baseline_eff
            print(f"🏆 Improvement: +{improvement:.3f} points/move ({improvement/baseline_eff*100:.1f}%)")
            print(f"Gap to 11.54 target: {11.54 - optimized_eff:.3f} points/move")
        else:
            print(f"📊 Baseline performs better")

    return results

if __name__ == "__main__":
    quick_weight_comparison()