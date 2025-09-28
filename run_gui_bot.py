#!/usr/bin/env python3
"""Launch the JED-2048 bot with the vaporwave pygame_gui interface."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from gui_enhanced_2048_bot import GUIEnhanced2048Bot


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the GUI-enhanced 2048 bot")
    parser.add_argument("--algorithm", type=str, default=None,
                        help="Algorithm identifier to load")
    parser.add_argument("--max-moves", type=int, default=500,
                        help="Maximum number of moves to play before stopping")
    parser.add_argument("--log-level", type=str, default="INFO",
                        help="Logging level for the bot")
    args = parser.parse_args()

    bot = GUIEnhanced2048Bot(gui_enabled=True,
                             headless=False,
                             debug=True,
                             log_level=args.log_level,
                             algorithm_id=args.algorithm)

    try:
        if not bot.connect_to_game():
            print("❌ Failed to connect to the 2048 game. Exiting.")
            return

        result = bot.play_autonomous_game(max_moves=args.max_moves)
        print("\n🎮 Game session complete")
        for key, value in result.items():
            print(f"   {key}: {value}")
    finally:
        bot.cleanup()


if __name__ == "__main__":
    main()
