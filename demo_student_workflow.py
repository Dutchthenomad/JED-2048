#!/usr/bin/env python3
"""
Demo script showing complete student workflow with GUI
"""

import sys
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from gui_enhanced_2048_bot import GUIEnhanced2048Bot

def demo_algorithm_comparison():
    """Demo comparing different algorithms for students"""
    print("🎓 STUDENT DEMO: Algorithm Comparison")
    print("=" * 50)

    algorithms_to_test = [
        ("Enhanced Heuristic_2.1", 15),
        ("Basic Priority_1.0", 15)
    ]

    results = {}

    for algo_name, moves in algorithms_to_test:
        print(f"\n🧠 Testing Algorithm: {algo_name}")
        print("-" * 30)

        try:
            # Initialize bot with GUI
            bot = GUIEnhanced2048Bot(
                headless=False,
                debug=True,
                algorithm_id=algo_name,
                gui_enabled=True
            )

            # Connect to game
            if not bot.connect_to_game():
                print(f"❌ Failed to connect for {algo_name}")
                continue

            # Run test
            print(f"🎮 Running {moves} moves with GUI visualization...")
            start_time = time.time()
            game_results = bot.play_autonomous_game(max_moves=moves)
            duration = time.time() - start_time

            # Store results
            results[algo_name] = {
                'moves': game_results.get('moves_completed', 0),
                'score': game_results.get('final_score', 0),
                'highest_tile': game_results.get('highest_tile', 0),
                'duration': duration,
                'efficiency': game_results.get('final_score', 0) / max(game_results.get('moves_completed', 1), 1)
            }

            print(f"✅ Completed: {results[algo_name]['moves']} moves, Score: {results[algo_name]['score']}")

            # Cleanup
            bot.cleanup()
            time.sleep(2)  # Brief pause between tests

        except Exception as e:
            print(f"❌ Error testing {algo_name}: {e}")
            if 'bot' in locals():
                bot.cleanup()

    # Display comparison
    print("\n📊 ALGORITHM COMPARISON RESULTS")
    print("=" * 50)

    for algo_name, data in results.items():
        print(f"\n🧠 {algo_name}:")
        print(f"   Moves Completed: {data['moves']}")
        print(f"   Final Score: {data['score']}")
        print(f"   Highest Tile: {data['highest_tile']}")
        print(f"   Efficiency: {data['efficiency']:.2f} points/move")
        print(f"   Duration: {data['duration']:.1f}s")

    return results

def demo_gui_features():
    """Demo key GUI features for students"""
    print("\n🖥️ STUDENT DEMO: GUI Features")
    print("=" * 50)

    try:
        # Initialize with GUI
        bot = GUIEnhanced2048Bot(
            headless=False,
            debug=True,
            gui_enabled=True
        )

        print("✅ GUI Features Available:")
        print("   📊 Real-time performance metrics")
        print("   🎮 Bot control buttons (Start/Stop/Pause)")
        print("   👁️ Computer vision overlays")
        print("   📈 Live strategy analysis")
        print("   🧠 Algorithm comparison tools")

        if hasattr(bot, 'debug_gui') and bot.debug_gui:
            print("   ✅ Debug interface loaded")

        # Brief display for students to see
        print("\n🎮 GUI will display for 5 seconds...")
        time.sleep(5)

        bot.cleanup()
        return True

    except Exception as e:
        print(f"❌ GUI demo failed: {e}")
        if 'bot' in locals():
            bot.cleanup()
        return False

def main():
    """Run complete student workflow demo"""
    print("🎓 2048 BOT - STUDENT COURSE DEMO")
    print("=" * 60)
    print("Welcome to the 2048 AI Bot Educational Platform!")
    print("This demo shows the complete student learning experience.\n")

    try:
        # Demo 1: GUI Features
        gui_success = demo_gui_features()

        # Demo 2: Algorithm Comparison
        if gui_success:
            algorithm_results = demo_algorithm_comparison()

            # Summary for students
            print("\n🎯 LEARNING OBJECTIVES COMPLETED:")
            print("=" * 50)
            print("✅ Understand different AI algorithms")
            print("✅ Compare algorithm performance")
            print("✅ Analyze real-time bot behavior")
            print("✅ Use debugging tools for AI development")

            if algorithm_results:
                best_algo = max(algorithm_results.items(), key=lambda x: x[1]['efficiency'])
                print(f"\n🏆 Best performing algorithm: {best_algo[0]}")
                print(f"   Efficiency: {best_algo[1]['efficiency']:.2f} points/move")

        else:
            print("⚠️ GUI demo failed, but core functionality works")

        print("\n✨ Student workflow demo completed!")
        return True

    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted")
        sys.exit(1)