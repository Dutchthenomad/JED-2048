#!/usr/bin/env python3
"""
Algorithm Comparison Demo with Organized Screenshots
Demonstrates the complete student workflow with screenshot organization
"""

import sys
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from gui_enhanced_2048_bot import GUIEnhanced2048Bot
from core.screenshot_manager import comparison_manager, screenshot_manager

def run_algorithm_comparison():
    """Run a complete algorithm comparison with organized screenshots"""
    print("🔬 ALGORITHM COMPARISON DEMO")
    print("=" * 50)
    print("This demo compares algorithms with organized screenshot storage\n")

    # Start comparison study
    comparison_id = comparison_manager.start_comparison("student_demo")
    print(f"📊 Started comparison: {comparison_id}")

    algorithms = [
        ("Enhanced Heuristic_2.1", 10),
        ("Basic Priority_1.0", 10)
    ]

    results = {}

    for algo_name, max_moves in algorithms:
        print(f"\n🧠 Testing: {algo_name}")
        print("-" * 30)

        try:
            # Initialize bot with GUI
            bot = GUIEnhanced2048Bot(
                headless=False,
                debug=True,
                algorithm_id=algo_name,
                gui_enabled=True
            )

            print(f"✅ Bot initialized with {algo_name}")

            # Connect to game
            if not bot.connect_to_game():
                print(f"❌ Failed to connect for {algo_name}")
                continue

            print(f"🎮 Running {max_moves} moves with live GUI...")

            # Run test with GUI
            start_time = time.time()
            game_results = bot.play_autonomous_game(max_moves=max_moves)
            duration = time.time() - start_time

            # Get screenshot session data
            session_screenshots = screenshot_manager.get_session_screenshots()

            # Store results
            results[algo_name] = {
                'moves': game_results.get('moves_completed', 0),
                'score': game_results.get('final_score', 0),
                'highest_tile': game_results.get('highest_tile', 0),
                'duration': duration,
                'screenshots': len(session_screenshots),
                'session_id': screenshot_manager.current_session.session_id if screenshot_manager.current_session else None
            }

            # Add to comparison
            if screenshot_manager.current_session:
                comparison_manager.add_algorithm_session(algo_name, screenshot_manager.current_session)

            print(f"✅ Completed: {results[algo_name]['moves']} moves")
            print(f"   Screenshots captured: {results[algo_name]['screenshots']}")

            # Cleanup
            bot.cleanup()
            time.sleep(2)

        except Exception as e:
            print(f"❌ Error testing {algo_name}: {e}")
            if 'bot' in locals():
                bot.cleanup()

    # Save comparison report
    report_path = comparison_manager.save_comparison_report()
    if report_path:
        print(f"\n📄 Comparison report saved: {report_path}")

    # Display results
    print(f"\n📊 COMPARISON RESULTS")
    print("=" * 50)

    for algo_name, data in results.items():
        efficiency = data['score'] / max(data['moves'], 1)
        print(f"\n🧠 {algo_name}:")
        print(f"   Moves: {data['moves']}")
        print(f"   Score: {data['score']}")
        print(f"   Highest Tile: {data['highest_tile']}")
        print(f"   Efficiency: {efficiency:.2f} points/move")
        print(f"   Screenshots: {data['screenshots']}")
        print(f"   Session ID: {data['session_id']}")

    # Show file organization
    print(f"\n📁 SCREENSHOT ORGANIZATION")
    print("=" * 50)
    print("Screenshots are organized in:")
    print(f"   temp/sessions/ - Individual algorithm sessions")
    print(f"   temp/algorithm_comparisons/{comparison_id}/ - This comparison")
    print("   Each session contains move-by-move screenshots")

    return results

def demo_screenshot_organization():
    """Demo the screenshot organization system"""
    print("\n📸 SCREENSHOT ORGANIZATION DEMO")
    print("=" * 50)

    # Show directory structure
    temp_dir = Path("temp")
    if temp_dir.exists():
        print("Current temp directory structure:")
        for item in temp_dir.rglob("*"):
            if item.is_file():
                rel_path = item.relative_to(temp_dir)
                print(f"   {rel_path}")

    # Show session info if available
    if screenshot_manager.current_session:
        session = screenshot_manager.current_session
        print(f"\nCurrent session: {session.session_id}")
        print(f"Algorithm: {session.algorithm_name}")
        print(f"Screenshots: {session.screenshot_count}")

def main():
    """Main demo function"""
    print("🎓 2048 BOT - ORGANIZED SCREENSHOT DEMO")
    print("=" * 60)

    try:
        # Run algorithm comparison
        results = run_algorithm_comparison()

        # Demo screenshot organization
        demo_screenshot_organization()

        print("\n✨ Screenshot organization demo completed!")
        print("\n🎯 EDUCATIONAL BENEFITS:")
        print("✅ Organized screenshot storage")
        print("✅ Algorithm comparison tracking")
        print("✅ Session-based organization")
        print("✅ Clean project structure")
        print("✅ Easy screenshot retrieval for analysis")

        return True

    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted")
        return False
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)