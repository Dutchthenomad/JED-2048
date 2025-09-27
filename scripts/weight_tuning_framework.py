#!/usr/bin/env python3
"""
Weight tuning framework for optimizing 2048 strategy performance
Tests different heuristic weight configurations with visible gameplay
"""

import sys
from pathlib import Path
import copy

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from complete_2048_bot import Complete2048Bot
from core.strategy import BasicStrategy

class WeightTuningFramework:
    """Framework for testing different heuristic weight configurations"""

    def __init__(self):
        self.baseline_weights = {
            'empty_tiles': 100.0,
            'merge_potential': 50.0,
            'corner_bonus': 200.0,
            'monotonicity': 30.0,
            'max_tile_value': 10.0
        }

        # Define weight configurations to test
        self.weight_configurations = {
            "baseline": self.baseline_weights,

            "empty_focus": {
                'empty_tiles': 200.0,      # Double emphasis on empty space
                'merge_potential': 75.0,   # Increase merge priority
                'corner_bonus': 150.0,     # Reduce corner obsession
                'monotonicity': 50.0,      # Increase monotonicity
                'max_tile_value': 10.0
            },

            "corner_aggressive": {
                'empty_tiles': 80.0,
                'merge_potential': 40.0,
                'corner_bonus': 400.0,     # Super aggressive corner strategy
                'monotonicity': 60.0,      # High monotonicity for corner builds
                'max_tile_value': 15.0
            },

            "merge_focused": {
                'empty_tiles': 120.0,
                'merge_potential': 150.0,  # Prioritize merges heavily
                'corner_bonus': 100.0,     # Lower corner priority
                'monotonicity': 40.0,
                'max_tile_value': 20.0     # Value high tiles more
            },

            "balanced_optimized": {
                'empty_tiles': 150.0,      # Increased from baseline
                'merge_potential': 100.0,  # Double merge value
                'corner_bonus': 250.0,     # Slight corner increase
                'monotonicity': 75.0,      # Much higher monotonicity
                'max_tile_value': 15.0     # Slight increase
            }
        }

    def test_weight_configuration(self, config_name: str, max_moves: int = 100):
        """Test a specific weight configuration with visible gameplay"""
        print(f"\n🎯 TESTING CONFIGURATION: {config_name.upper()}")
        print("=" * 60)

        weights = self.weight_configurations[config_name]
        print(f"Weight configuration:")
        for key, value in weights.items():
            print(f"   {key}: {value}")

        # Create bot with visible browser
        bot = Complete2048Bot(
            headless=False,  # Always visible as requested
            debug=True
        )

        try:
            # Update strategy weights
            bot.strategy.weights = copy.deepcopy(weights)

            print(f"\n🌐 Connecting to game...")
            if not bot.connect_to_game():
                print("❌ Failed to connect to game")
                return None

            print(f"🚀 Starting {config_name} test game (max {max_moves} moves)...")
            results = bot.play_autonomous_game(max_moves=max_moves)

            # Calculate performance metrics
            moves = results.get('moves_completed', 0)
            final_score = results.get('final_score', 0)
            highest_tile = results.get('highest_tile', 0)
            duration = results.get('duration_seconds', 0)
            efficiency = final_score / moves if moves > 0 else 0

            performance_data = {
                'config_name': config_name,
                'weights': weights,
                'moves': moves,
                'score': final_score,
                'highest_tile': highest_tile,
                'efficiency': efficiency,
                'duration': duration,
                'speed': moves/duration if duration > 0 else 0
            }

            print(f"\n📊 {config_name.upper()} RESULTS:")
            print(f"   Moves: {moves}")
            print(f"   Score: {final_score}")
            print(f"   Highest tile: {highest_tile}")
            print(f"   Efficiency: {efficiency:.3f} points/move")
            print(f"   Duration: {duration:.1f}s")
            print(f"   Speed: {performance_data['speed']:.2f} moves/s")

            return performance_data

        except KeyboardInterrupt:
            print(f"\n⏹️  {config_name} test interrupted by user")
            bot.cleanup()
            return None
        except Exception as e:
            print(f"\n❌ {config_name} test failed: {e}")
            bot.cleanup()
            return None
        finally:
            bot.cleanup()

    def run_weight_comparison(self, max_moves_per_test: int = 50):
        """Run comparison tests across different weight configurations"""
        print("🧪 HEURISTIC WEIGHT TUNING COMPARISON")
        print("=" * 70)
        print("🖥️  All tests running in VISIBLE mode")
        print(f"⏱️  Max {max_moves_per_test} moves per test for quick comparison")
        print("")

        results = []
        baseline_efficiency = None

        for config_name in ["baseline", "empty_focus", "balanced_optimized", "merge_focused"]:
            print(f"\n{'='*70}")
            result = self.test_weight_configuration(config_name, max_moves_per_test)

            if result:
                results.append(result)
                if config_name == "baseline":
                    baseline_efficiency = result['efficiency']

            print(f"\n⏳ Waiting 3 seconds before next test...")
            import time
            time.sleep(3)

        # Performance comparison
        print(f"\n{'='*70}")
        print("📊 WEIGHT TUNING COMPARISON RESULTS")
        print("="*70)

        if results:
            # Sort by efficiency
            results.sort(key=lambda x: x['efficiency'], reverse=True)

            print(f"{'Rank':<5} {'Configuration':<20} {'Efficiency':<12} {'Score':<8} {'Tile':<6} {'Improvement':<12}")
            print("-" * 70)

            for i, result in enumerate(results, 1):
                config = result['config_name']
                efficiency = result['efficiency']
                score = result['score']
                tile = result['highest_tile']

                if baseline_efficiency and baseline_efficiency > 0:
                    improvement = ((efficiency - baseline_efficiency) / baseline_efficiency) * 100
                    improvement_str = f"{improvement:+.1f}%"
                else:
                    improvement_str = "N/A"

                print(f"{i:<5} {config:<20} {efficiency:<12.3f} {score:<8} {tile:<6} {improvement_str:<12}")

            best_config = results[0]
            print(f"\n🏆 BEST CONFIGURATION: {best_config['config_name'].upper()}")
            print(f"   Efficiency: {best_config['efficiency']:.3f} points/move")
            print(f"   Target baseline: 11.54 points/move")
            remaining_gap = 11.54 - best_config['efficiency']
            print(f"   Remaining gap: {remaining_gap:.3f} points/move")

        return results

def main():
    """Main weight tuning execution"""
    framework = WeightTuningFramework()

    print("🎯 2048 STRATEGY WEIGHT TUNING FRAMEWORK")
    print("=" * 50)
    print("🔧 Optimizing heuristic weights for maximum performance")
    print("🖥️  All gameplay will be visible in browser window")
    print("")

    # Run comparison with shorter games for quick testing
    results = framework.run_weight_comparison(max_moves_per_test=40)

    print(f"\n🎉 WEIGHT TUNING COMPLETE!")
    print("Ready to implement best configuration for enhanced performance.")

if __name__ == "__main__":
    main()