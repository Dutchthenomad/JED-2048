#!/usr/bin/env python3
"""
2048 Bot Runner
Runs the complete automated 2048 bot with manual controls.

Complete integration: Vision + Strategy + Browser Automation
"""

import sys
import time
import signal
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.game_bot import GameBot
from core.browser_controller import BrowserType

class BotRunner:
    """Manages bot execution with user controls"""

    def __init__(self):
        self.bot = None
        self.running = False

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n🛑 Interrupt received - stopping bot...")
        if self.bot:
            self.bot.stop_bot()
        self.running = False

    def run_single_game(self, game_url: str, debug: bool = False):
        """Run a single game with the bot"""
        print("🤖 Starting Single Game Mode")
        print("=" * 40)

        try:
            # Create bot
            self.bot = GameBot(
                browser_type=BrowserType.FIREFOX,
                headless=False,
                debug_mode=debug
            )

            # Start bot
            if not self.bot.start_bot(game_url):
                print("❌ Failed to start bot")
                return

            print("✅ Bot started successfully")
            print("🎮 Playing game...")

            # Play one complete game
            session = self.bot.play_game()

            if session and session.completed:
                print(f"\n🎯 Game Results:")
                print(f"   Score: {session.final_score}")
                print(f"   Moves: {session.moves}")
                print(f"   Efficiency: {session.efficiency:.2f} points/move")
                print(f"   Highest Tile: {session.highest_tile}")
                print(f"   Duration: {session.end_time - session.start_time}")

                # Compare to baseline
                baseline_efficiency = 11.54  # Your human baseline
                if session.efficiency > baseline_efficiency:
                    print(f"🎉 Exceeded baseline efficiency! ({session.efficiency:.2f} > {baseline_efficiency})")
                else:
                    print(f"📈 Efficiency below baseline ({session.efficiency:.2f} vs {baseline_efficiency})")

            else:
                print("❌ Game did not complete successfully")

        except KeyboardInterrupt:
            print("\n⏹️  Game interrupted by user")
        except Exception as e:
            print(f"❌ Error during game: {e}")
        finally:
            if self.bot:
                self.bot.stop_bot()

    def run_continuous(self, game_url: str, max_games: int = 5, debug: bool = False):
        """Run multiple games continuously"""
        print("🔄 Starting Continuous Mode")
        print("=" * 40)
        print(f"Target: {max_games} games")
        print("Press Ctrl+C to stop gracefully\n")

        # Setup signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        self.running = True

        try:
            # Create bot
            self.bot = GameBot(
                browser_type=BrowserType.FIREFOX,
                headless=False,
                debug_mode=debug
            )

            # Start bot
            if not self.bot.start_bot(game_url):
                print("❌ Failed to start bot")
                return

            # Play multiple games
            for game_num in range(1, max_games + 1):
                if not self.running:
                    break

                print(f"\n🎮 Game {game_num}/{max_games}")
                print("-" * 30)

                session = self.bot.play_game()

                if session and session.completed:
                    print(f"✅ Game {game_num} completed:")
                    print(f"   Score: {session.final_score}")
                    print(f"   Moves: {session.moves}")
                    print(f"   Efficiency: {session.efficiency:.2f}")
                else:
                    print(f"❌ Game {game_num} failed")

                # Brief pause between games
                if self.running and game_num < max_games:
                    print("⏸️  Brief pause before next game...")
                    time.sleep(2)

            # Show final statistics
            self._show_statistics()

        except KeyboardInterrupt:
            print("\n⏹️  Continuous mode interrupted")
        except Exception as e:
            print(f"❌ Error in continuous mode: {e}")
        finally:
            if self.bot:
                self.bot.stop_bot()

    def _show_statistics(self):
        """Show bot performance statistics"""
        if not self.bot:
            return

        stats = self.bot.get_statistics()

        if "message" in stats:
            print(f"\n📊 Statistics: {stats['message']}")
            return

        print(f"\n📊 Bot Performance Statistics")
        print("=" * 40)
        print(f"Games Played: {stats['total_games']}")
        print(f"Total Score: {stats['total_score']}")
        print(f"Total Moves: {stats['total_moves']}")
        print(f"Average Score: {stats['average_score']:.1f}")
        print(f"Average Moves: {stats['average_moves']:.1f}")
        print(f"Average Efficiency: {stats['average_efficiency']:.2f} points/move")
        print(f"Best Score: {stats['best_score']}")
        print(f"Best Efficiency: {stats['best_efficiency']:.2f}")
        print(f"Highest Tile: {stats['highest_tile']}")

        if stats['vision_failures'] > 0 or stats['action_failures'] > 0:
            print(f"\n⚠️  Failures:")
            print(f"Vision Failures: {stats['vision_failures']}")
            print(f"Action Failures: {stats['action_failures']}")

def main():
    """Main bot runner interface"""
    print("🤖 2048 Autonomous Bot")
    print("=" * 50)
    print("Complete automation: Vision + Strategy + Browser Control\n")

    # Default game URL
    default_url = "https://play2048.co/"

    print("Available modes:")
    print("1. Single game (test run)")
    print("2. Continuous play (multiple games)")
    print("3. Debug single game")

    try:
        choice = input("\nSelect mode (1-3): ").strip()

        if choice == "1":
            runner = BotRunner()
            runner.run_single_game(default_url, debug=False)

        elif choice == "2":
            try:
                num_games = int(input("Number of games (1-10): ").strip())
                num_games = max(1, min(10, num_games))  # Limit range
            except:
                num_games = 3

            runner = BotRunner()
            runner.run_continuous(default_url, num_games, debug=False)

        elif choice == "3":
            runner = BotRunner()
            runner.run_single_game(default_url, debug=True)

        else:
            print("Invalid choice")
            return

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()