#!/usr/bin/env python3
"""
Run the Complete2048Bot non-headless for exactly 16 moves.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from complete_2048_bot import Complete2048Bot


def main():
    url = "https://2048game.com/"
    bot = Complete2048Bot(headless=False, debug=True)
    try:
        print("🌐 Connecting to:", url)
        if not bot.connect_to_game(url=url):
            print("❌ Failed to connect to game")
            return 1
        print("🚀 Playing 16 moves...")
        results = bot.play_autonomous_game(max_moves=16)
        print("\n📊 Results (16 moves):")
        print(results)
        return 0
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        return 130
    except Exception as e:
        print("❌ Run failed:", e)
        return 2
    finally:
        bot.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())

