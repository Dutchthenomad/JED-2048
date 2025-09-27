#!/usr/bin/env python3
"""
Production Bot Runner
Main entry point for production 2048 bot execution
"""

import sys
import argparse
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from complete_2048_bot import Complete2048Bot
from production.performance_monitor import PerformanceMonitor

def load_config(config_path: str) -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Config file not found: {config_path}")
        return get_default_config()
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return get_default_config()

def get_default_config() -> dict:
    """Get default production configuration"""
    return {
        "environment": "production",
        "bot": {
            "headless": True,
            "debug": False,
            "log_level": "INFO",
            "browser_type": "chromium",
            "max_moves": 200
        },
        "performance": {
            "monitoring_enabled": True,
            "log_interval": 5.0,
            "enable_alerts": True
        }
    }

def run_production_bot(config: dict, games: int = 1):
    """Run bot in production mode"""
    print("🚀 PRODUCTION 2048 BOT")
    print("=" * 50)
    print(f"🎯 Games to play: {games}")
    print(f"⚙️ Configuration: {config['environment']}")
    print("")

    # Setup performance monitoring
    perf_config = config.get('performance', {})
    monitor = None

    if perf_config.get('monitoring_enabled', True):
        monitor = PerformanceMonitor(
            log_interval=perf_config.get('log_interval', 5.0),
            enable_alerts=perf_config.get('enable_alerts', True)
        )
        monitor.start_monitoring()
        print("📊 Performance monitoring enabled")

    results = []
    successful_games = 0

    try:
        for game_num in range(games):
            print(f"\n🎮 Game {game_num + 1}/{games}")
            print("-" * 30)

            # Initialize bot with config
            bot_config = config.get('bot', {})
            bot = Complete2048Bot(
                headless=bot_config.get('headless', True),
                debug=bot_config.get('debug', False),
                log_level=bot_config.get('log_level', 'INFO')
            )

            try:
                # Connect to game
                if bot.connect_to_game():
                    # Play game
                    game_result = bot.play_autonomous_game(
                        max_moves=bot_config.get('max_moves', 200)
                    )

                    # Update performance monitor
                    if monitor:
                        monitor.update_bot_metrics(
                            move_count=game_result.get('moves_completed', 0),
                            game_score=game_result.get('final_score', 0)
                        )

                    results.append(game_result)
                    successful_games += 1

                    print(f"✅ Game completed:")
                    print(f"   Moves: {game_result.get('moves_completed', 0)}")
                    print(f"   Score: {game_result.get('final_score', 0)}")
                    print(f"   Highest tile: {game_result.get('highest_tile', 0)}")

                else:
                    print("❌ Failed to connect to game")

            except Exception as e:
                print(f"❌ Game {game_num + 1} failed: {e}")

            finally:
                bot.cleanup()

        # Summary
        print(f"\n{'='*50}")
        print("📊 PRODUCTION RUN SUMMARY")
        print("="*50)

        if successful_games > 0:
            total_moves = sum(r.get('moves_completed', 0) for r in results)
            total_score = sum(r.get('final_score', 0) for r in results)
            avg_efficiency = total_score / max(total_moves, 1)

            print(f"✅ Successful games: {successful_games}/{games}")
            print(f"📈 Total moves: {total_moves}")
            print(f"🎯 Total score: {total_score}")
            print(f"⚡ Average efficiency: {avg_efficiency:.2f} points/move")

            # Best game
            if results:
                best_game = max(results, key=lambda x: x.get('final_score', 0))
                print(f"🏆 Best game score: {best_game.get('final_score', 0)}")

        else:
            print("❌ No successful games completed")

        # Performance report
        if monitor:
            print(f"\n📊 Performance Report:")
            current_metrics = monitor.get_current_metrics()
            if current_metrics:
                print(f"   Memory usage: {current_metrics.memory_mb:.1f} MB")
                print(f"   CPU usage: {current_metrics.cpu_percent:.1f}%")

            # Export performance data
            timestamp = int(time.time())
            report_file = f"reports/production_run_{timestamp}.json"
            monitor.export_metrics(report_file)
            print(f"   📁 Detailed report: {report_file}")

    finally:
        if monitor:
            monitor.stop_monitoring()

    return results

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Production 2048 Bot Runner")
    parser.add_argument("--config", default="config/production.json",
                       help="Configuration file path")
    parser.add_argument("--games", type=int, default=1,
                       help="Number of games to play")
    parser.add_argument("--production", action="store_true",
                       help="Use production defaults")

    args = parser.parse_args()

    # Load configuration
    if args.production or not Path(args.config).exists():
        config = get_default_config()
        print(f"📋 Using default production configuration")
    else:
        config = load_config(args.config)
        print(f"📋 Loaded configuration from: {args.config}")

    # Create necessary directories
    Path("logs").mkdir(exist_ok=True)
    Path("reports").mkdir(exist_ok=True)

    # Run production bot
    import time
    results = run_production_bot(config, args.games)

    print(f"\n🎉 Production run completed!")
    return len([r for r in results if r.get('final_score', 0) > 0]) > 0

if __name__ == "__main__":
    import time
    success = main()
    exit_code = 0 if success else 1
    sys.exit(exit_code)