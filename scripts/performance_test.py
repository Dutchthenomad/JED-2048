#!/usr/bin/env python3
"""
Performance Test Suite for 2048 Bot
Comprehensive performance testing and optimization analysis
"""

import sys
from pathlib import Path
import time
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from complete_2048_bot import Complete2048Bot
from production.performance_monitor import PerformanceMonitor
import logging

def performance_baseline_test():
    """Run baseline performance test"""
    print("🚀 PERFORMANCE BASELINE TEST")
    print("=" * 60)
    print("📊 Testing bot performance with monitoring enabled")
    print("")

    # Initialize performance monitor
    monitor = PerformanceMonitor(log_interval=2.0, enable_alerts=True)

    # Add performance alert handler
    def performance_alert(message, metrics):
        print(f"⚠️  PERFORMANCE ALERT: {message}")

    monitor.add_alert_callback(performance_alert)

    # Start monitoring
    monitor.start_monitoring()
    time.sleep(1)  # Let monitoring stabilize

    try:
        # Test different configurations
        configurations = [
            {"name": "Headless Optimized", "headless": True, "debug": False, "log_level": "WARNING"},
            {"name": "Visible Debug", "headless": False, "debug": True, "log_level": "INFO"},
        ]

        results = []

        for config in configurations:
            print(f"\n🧪 Testing Configuration: {config['name']}")
            print(f"   Settings: {config}")

            config_start_time = time.time()

            # Initialize bot with current configuration
            bot = Complete2048Bot(
                headless=config['headless'],
                debug=config['debug'],
                log_level=config['log_level']
            )

            try:
                # Connection test
                print("   🌐 Testing connection...")
                connection_start = time.time()
                connection_success = bot.connect_to_game()
                connection_time = time.time() - connection_start

                if connection_success:
                    print(f"   ✅ Connected in {connection_time:.2f}s")

                    # Performance test with limited moves
                    print("   🎮 Running performance game (20 moves)...")
                    game_start = time.time()

                    # Track performance metrics during game
                    initial_metrics = monitor.get_current_metrics()

                    # Play short game for performance testing
                    game_results = bot.play_autonomous_game(max_moves=20)

                    game_duration = time.time() - game_start
                    final_metrics = monitor.get_current_metrics()

                    # Update monitor with final bot metrics
                    monitor.update_bot_metrics(
                        move_count=game_results.get('moves_completed', 0),
                        game_score=game_results.get('final_score', 0)
                    )

                    # Calculate performance metrics
                    config_result = {
                        'configuration': config['name'],
                        'connection_time': connection_time,
                        'game_duration': game_duration,
                        'moves_completed': game_results.get('moves_completed', 0),
                        'final_score': game_results.get('final_score', 0),
                        'efficiency': game_results.get('final_score', 0) / max(game_results.get('moves_completed', 1), 1),
                        'moves_per_second': game_results.get('moves_completed', 0) / max(game_duration, 0.1),
                        'memory_usage_mb': final_metrics.memory_mb if final_metrics else 0,
                        'cpu_percent': final_metrics.cpu_percent if final_metrics else 0,
                        'success': True
                    }

                    print(f"   📊 Results:")
                    print(f"      Moves: {config_result['moves_completed']}")
                    print(f"      Score: {config_result['final_score']}")
                    print(f"      Efficiency: {config_result['efficiency']:.2f} points/move")
                    print(f"      Speed: {config_result['moves_per_second']:.2f} moves/sec")
                    print(f"      Memory: {config_result['memory_usage_mb']:.1f} MB")
                    print(f"      CPU: {config_result['cpu_percent']:.1f}%")

                else:
                    print("   ❌ Connection failed")
                    config_result = {
                        'configuration': config['name'],
                        'connection_time': connection_time,
                        'success': False,
                        'error': 'Connection failed'
                    }

                results.append(config_result)

            except Exception as e:
                print(f"   ❌ Configuration failed: {e}")
                config_result = {
                    'configuration': config['name'],
                    'success': False,
                    'error': str(e)
                }
                results.append(config_result)

            finally:
                bot.cleanup()
                time.sleep(2)  # Cool down between tests

        # Performance comparison
        print(f"\n{'='*60}")
        print("📊 PERFORMANCE COMPARISON")
        print("="*60)

        successful_results = [r for r in results if r.get('success', False)]

        if len(successful_results) >= 2:
            print(f"{'Configuration':<20} {'Moves/sec':<10} {'Memory':<10} {'CPU':<8} {'Efficiency':<12}")
            print("-" * 60)

            for result in successful_results:
                config_name = result['configuration'][:19]
                moves_sec = f"{result.get('moves_per_second', 0):.2f}"
                memory_mb = f"{result.get('memory_usage_mb', 0):.1f}MB"
                cpu_pct = f"{result.get('cpu_percent', 0):.1f}%"
                efficiency = f"{result.get('efficiency', 0):.2f}"

                print(f"{config_name:<20} {moves_sec:<10} {memory_mb:<10} {cpu_pct:<8} {efficiency:<12}")

            # Find best configuration
            best_speed = max(successful_results, key=lambda x: x.get('moves_per_second', 0))
            best_memory = min(successful_results, key=lambda x: x.get('memory_usage_mb', float('inf')))
            best_efficiency = max(successful_results, key=lambda x: x.get('efficiency', 0))

            print(f"\n🏆 Performance Winners:")
            print(f"   Fastest: {best_speed['configuration']} ({best_speed.get('moves_per_second', 0):.2f} moves/sec)")
            print(f"   Most Memory Efficient: {best_memory['configuration']} ({best_memory.get('memory_usage_mb', 0):.1f} MB)")
            print(f"   Best Game Efficiency: {best_efficiency['configuration']} ({best_efficiency.get('efficiency', 0):.2f} points/move)")

        # Get system-wide performance report
        print(f"\n📋 SYSTEM PERFORMANCE REPORT")
        print("="*40)
        performance_report = monitor.get_performance_report()

        print(f"System Info:")
        sys_info = performance_report.get('system_info', {})
        print(f"   CPU Cores: {sys_info.get('cpu_count', 'Unknown')}")
        print(f"   Total Memory: {sys_info.get('memory_total_mb', 0):.0f} MB")
        print(f"   Platform: {sys_info.get('platform', 'Unknown')}")

        print(f"\nMonitoring Summary:")
        perf_summary = performance_report.get('performance_summary', {})
        print(f"   Duration: {perf_summary.get('monitoring_duration', 0):.1f} seconds")
        print(f"   Samples: {perf_summary.get('total_samples', 0)}")

        # Get optimization suggestions
        print(f"\n💡 OPTIMIZATION SUGGESTIONS")
        print("="*40)
        suggestions = monitor.optimize_settings()
        for suggestion in suggestions.get("suggestions", []):
            print(f"   • {suggestion}")

        # Export detailed results
        timestamp = int(time.time())
        export_file = f"performance_report_{timestamp}.json"

        export_data = {
            'test_results': results,
            'performance_report': performance_report,
            'optimization_suggestions': suggestions,
            'timestamp': timestamp
        }

        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"\n📁 Detailed report exported to: {export_file}")

        return results

    except KeyboardInterrupt:
        print("\n⏹️ Performance test interrupted by user")
        return []

    finally:
        monitor.stop_monitoring()
        print("\n✅ Performance testing completed")

def memory_stress_test():
    """Test memory usage under continuous operation"""
    print("\n🧠 MEMORY STRESS TEST")
    print("=" * 40)

    monitor = PerformanceMonitor(log_interval=1.0, enable_alerts=True)
    monitor.start_monitoring()

    try:
        bot = Complete2048Bot(headless=True, debug=False)

        if bot.connect_to_game():
            print("🎮 Running continuous games to test memory stability...")

            for game_num in range(5):
                print(f"   Game {game_num + 1}/5...")

                initial_memory = monitor.get_current_metrics().memory_mb

                # Play short game
                bot.play_autonomous_game(max_moves=15)

                final_memory = monitor.get_current_metrics().memory_mb
                memory_increase = final_memory - initial_memory

                print(f"   Memory: {initial_memory:.1f} → {final_memory:.1f} MB (Δ{memory_increase:+.1f})")

                # Reset game for next iteration
                bot.controller.reset_game()
                time.sleep(1)

        bot.cleanup()

        avg_metrics = monitor.get_average_metrics(300.0)  # 5 minute window
        print(f"\n📊 Average Memory Usage: {avg_metrics.get('memory_mb', 0):.1f} MB")

    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    print("🧪 2048 BOT PERFORMANCE TEST SUITE")
    print("=" * 70)
    print("🔬 Comprehensive performance analysis and optimization testing")
    print("")

    try:
        # Run baseline performance test
        baseline_results = performance_baseline_test()

        # Run memory stress test
        memory_stress_test()

        print(f"\n🎉 PERFORMANCE TESTING COMPLETE!")
        print("📊 Check exported JSON files for detailed analysis")

    except Exception as e:
        print(f"\n❌ Performance testing failed: {e}")
        import traceback
        traceback.print_exc()