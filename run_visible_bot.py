#!/usr/bin/env python3
"""
Run the complete 2048 bot in visible mode for performance validation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from complete_2048_bot import Complete2048Bot

def run_visible_performance_test():
    """Run bot in visible mode for performance measurement"""
    print("🎮 VISIBLE 2048 BOT - PERFORMANCE VALIDATION")
    print("=" * 60)
    print("🖥️  Running in VISIBLE mode - you should see browser window")
    print("⏱️  Performance measurement against 11.54 points/move baseline")
    print("")

    # Initialize bot in non-headless mode
    bot = Complete2048Bot(
        headless=False,  # Show browser window
        debug=True       # Show detailed output
    )

    try:
        # Connect to the game first
        print("🌐 Connecting to 2048 game...")
        if not bot.connect_to_game():
            print("❌ Failed to connect to game")
            return None

        # Play one complete game
        print("🚀 Starting performance validation game...")
        results = bot.play_autonomous_game(max_moves=500)  # Allow up to 500 moves

        print("\n" + "=" * 60)
        print("📊 PERFORMANCE ANALYSIS")
        print("=" * 60)

        # Extract key metrics
        moves = results.get('moves_completed', 0)
        final_score = results.get('final_score', 0)
        highest_tile = results.get('highest_tile', 0)
        duration = results.get('duration_seconds', 0)

        # Calculate efficiency
        efficiency = final_score / moves if moves > 0 else 0
        baseline = 11.54  # Your human baseline

        print(f"🎯 Game Results:")
        print(f"   Total moves: {moves}")
        print(f"   Final score: {final_score}")
        print(f"   Highest tile: {highest_tile}")
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Speed: {moves/duration:.2f} moves/second" if duration > 0 else "   Speed: N/A")

        print(f"\n📈 Performance vs Baseline:")
        print(f"   Bot efficiency: {efficiency:.2f} points/move")
        print(f"   Human baseline: {baseline:.2f} points/move")

        if efficiency >= baseline:
            print(f"   🏆 SUCCESS: Bot exceeds human baseline by {efficiency - baseline:.2f}")
        else:
            print(f"   📊 Result: Bot is {baseline - efficiency:.2f} below human baseline")

        performance_ratio = (efficiency / baseline) * 100 if baseline > 0 else 0
        print(f"   📊 Performance ratio: {performance_ratio:.1f}% of human baseline")

        return results

    except KeyboardInterrupt:
        print("\n⏹️  Performance test interrupted by user")
        bot.cleanup()
    except Exception as e:
        print(f"\n❌ Performance test failed: {e}")
        bot.cleanup()

if __name__ == "__main__":
    run_visible_performance_test()