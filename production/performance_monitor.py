#!/usr/bin/env python3
"""
Performance Monitor for 2048 Bot
Real-time monitoring of resource usage, performance metrics, and optimization
"""

import time
import psutil
import os
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import logging

@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    disk_io_read: int
    disk_io_write: int
    network_sent: int
    network_recv: int

    # Bot-specific metrics
    move_count: int = 0
    game_score: int = 0
    efficiency: float = 0.0
    fps: float = 0.0
    screenshot_time: float = 0.0
    analysis_time: float = 0.0
    strategy_time: float = 0.0

class PerformanceMonitor:
    """Real-time performance monitoring and optimization"""

    def __init__(self, log_interval: float = 5.0, enable_alerts: bool = True):
        """
        Initialize performance monitor

        Args:
            log_interval: Seconds between performance logs
            enable_alerts: Enable performance alert system
        """
        self.log_interval = log_interval
        self.enable_alerts = enable_alerts
        self.monitoring = False
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history = 1000  # Keep last 1000 measurements

        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,        # CPU usage %
            'memory_mb': 1000.0,        # Memory usage MB
            'memory_percent': 75.0,     # Memory usage %
            'screenshot_time': 2.0,     # Screenshot time seconds
            'analysis_time': 1.0,       # Analysis time seconds
            'strategy_time': 0.5,       # Strategy time seconds
            'fps': 0.5                  # Minimum FPS (moves per second)
        }

        # System info
        self.process = psutil.Process(os.getpid())
        self.system = psutil.virtual_memory()

        # Monitoring thread
        self.monitor_thread = None
        self.stop_event = threading.Event()

        # Alert callbacks
        self.alert_callbacks: List[Callable] = []

        # Setup logging
        self.logger = logging.getLogger("performance_monitor")

    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self.monitoring:
            return

        self.monitoring = True
        self.stop_event.clear()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("🚀 Performance monitoring started")

    def stop_monitoring(self):
        """Stop performance monitoring"""
        if not self.monitoring:
            return

        self.monitoring = False
        self.stop_event.set()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        self.logger.info("⏹️ Performance monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self.stop_event.wait(self.log_interval):
            try:
                metrics = self._collect_metrics()
                self._process_metrics(metrics)
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        # System metrics
        cpu_percent = self.process.cpu_percent()
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_percent = self.process.memory_percent()

        # I/O metrics (if available)
        try:
            io_counters = self.process.io_counters()
            disk_read = io_counters.read_bytes
            disk_write = io_counters.write_bytes
        except (AttributeError, OSError):
            disk_read = disk_write = 0

        # Network metrics (system-wide)
        try:
            net_io = psutil.net_io_counters()
            net_sent = net_io.bytes_sent
            net_recv = net_io.bytes_recv
        except (AttributeError, OSError):
            net_sent = net_recv = 0

        return PerformanceMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            memory_percent=memory_percent,
            disk_io_read=disk_read,
            disk_io_write=disk_write,
            network_sent=net_sent,
            network_recv=net_recv
        )

    def _process_metrics(self, metrics: PerformanceMetrics):
        """Process and store metrics"""
        # Add to history
        self.metrics_history.append(metrics)

        # Trim history if too long
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]

        # Check thresholds
        if self.enable_alerts:
            self._check_alerts(metrics)

        # Log significant changes
        self._log_metrics(metrics)

    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check performance thresholds and trigger alerts"""
        alerts = []

        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")

        if metrics.memory_mb > self.thresholds['memory_mb']:
            alerts.append(f"High memory usage: {metrics.memory_mb:.1f} MB")

        if metrics.memory_percent > self.thresholds['memory_percent']:
            alerts.append(f"High memory percentage: {metrics.memory_percent:.1f}%")

        if metrics.screenshot_time > self.thresholds['screenshot_time']:
            alerts.append(f"Slow screenshot: {metrics.screenshot_time:.2f}s")

        if metrics.analysis_time > self.thresholds['analysis_time']:
            alerts.append(f"Slow analysis: {metrics.analysis_time:.2f}s")

        if metrics.strategy_time > self.thresholds['strategy_time']:
            alerts.append(f"Slow strategy: {metrics.strategy_time:.2f}s")

        if metrics.fps > 0 and metrics.fps < self.thresholds['fps']:
            alerts.append(f"Low FPS: {metrics.fps:.2f}")

        # Trigger alert callbacks
        for alert in alerts:
            self.logger.warning(f"⚠️ Performance Alert: {alert}")
            for callback in self.alert_callbacks:
                try:
                    callback(alert, metrics)
                except Exception as e:
                    self.logger.error(f"Alert callback error: {e}")

    def _log_metrics(self, metrics: PerformanceMetrics):
        """Log performance metrics"""
        self.logger.debug(
            f"📊 CPU: {metrics.cpu_percent:.1f}% | "
            f"Memory: {metrics.memory_mb:.1f}MB ({metrics.memory_percent:.1f}%) | "
            f"Moves: {metrics.move_count} | "
            f"Score: {metrics.game_score} | "
            f"Efficiency: {metrics.efficiency:.2f}"
        )

    def update_bot_metrics(self, move_count: int = 0, game_score: int = 0,
                          screenshot_time: float = 0.0, analysis_time: float = 0.0,
                          strategy_time: float = 0.0):
        """Update bot-specific performance metrics"""
        if self.metrics_history:
            latest = self.metrics_history[-1]
            latest.move_count = move_count
            latest.game_score = game_score
            latest.screenshot_time = screenshot_time
            latest.analysis_time = analysis_time
            latest.strategy_time = strategy_time

            # Calculate efficiency and FPS
            if move_count > 0:
                latest.efficiency = game_score / move_count

            # Calculate FPS from recent measurements
            if len(self.metrics_history) >= 2:
                time_diff = latest.timestamp - self.metrics_history[-2].timestamp
                move_diff = latest.move_count - self.metrics_history[-2].move_count
                if time_diff > 0:
                    latest.fps = move_diff / time_diff

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get latest performance metrics"""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_average_metrics(self, window_seconds: float = 60.0) -> Dict:
        """Get average metrics over time window"""
        if not self.metrics_history:
            return {}

        current_time = time.time()
        window_metrics = [
            m for m in self.metrics_history
            if current_time - m.timestamp <= window_seconds
        ]

        if not window_metrics:
            return {}

        # Calculate averages
        avg = {
            'cpu_percent': sum(m.cpu_percent for m in window_metrics) / len(window_metrics),
            'memory_mb': sum(m.memory_mb for m in window_metrics) / len(window_metrics),
            'memory_percent': sum(m.memory_percent for m in window_metrics) / len(window_metrics),
            'efficiency': sum(m.efficiency for m in window_metrics) / len(window_metrics),
            'fps': sum(m.fps for m in window_metrics) / len(window_metrics),
            'screenshot_time': sum(m.screenshot_time for m in window_metrics) / len(window_metrics),
            'analysis_time': sum(m.analysis_time for m in window_metrics) / len(window_metrics),
            'strategy_time': sum(m.strategy_time for m in window_metrics) / len(window_metrics),
            'sample_count': len(window_metrics),
            'window_seconds': window_seconds
        }

        return avg

    def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        if not self.metrics_history:
            return {"error": "No metrics available"}

        current = self.get_current_metrics()
        avg_1min = self.get_average_metrics(60.0)
        avg_5min = self.get_average_metrics(300.0)

        # System information
        system_info = {
            'cpu_count': psutil.cpu_count(),
            'memory_total_mb': psutil.virtual_memory().total / 1024 / 1024,
            'platform': os.name,
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        }

        # Performance summary
        performance_summary = {
            'monitoring_duration': time.time() - self.metrics_history[0].timestamp if self.metrics_history else 0,
            'total_samples': len(self.metrics_history),
            'current_metrics': asdict(current) if current else {},
            'average_1min': avg_1min,
            'average_5min': avg_5min,
            'thresholds': self.thresholds
        }

        return {
            'system_info': system_info,
            'performance_summary': performance_summary,
            'timestamp': time.time()
        }

    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        report = self.get_performance_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        self.logger.info(f"📁 Metrics exported to {filepath}")

    def add_alert_callback(self, callback: Callable):
        """Add callback function for performance alerts"""
        self.alert_callbacks.append(callback)

    def optimize_settings(self) -> Dict[str, str]:
        """Analyze performance and suggest optimizations"""
        suggestions = []

        current = self.get_current_metrics()
        if not current:
            return {"suggestions": ["Start monitoring to get optimization suggestions"]}

        # Memory optimization
        if current.memory_mb > 500:
            suggestions.append("Consider enabling headless mode to reduce memory usage")
            suggestions.append("Disable debug mode to reduce screenshot storage")

        # CPU optimization
        if current.cpu_percent > 60:
            suggestions.append("Consider using Chromium browser for better performance")
            suggestions.append("Reduce screenshot frequency or quality")

        # Speed optimization
        if current.screenshot_time > 1.0:
            suggestions.append("Switch to headless mode for faster screenshots")

        if current.analysis_time > 0.5:
            suggestions.append("Vision system may be overloaded - check image quality")

        if current.strategy_time > 0.2:
            suggestions.append("Strategy calculation is slow - consider simplifying weights")

        if current.fps < 1.0 and current.move_count > 0:
            suggestions.append("Overall performance is slow - consider system optimization")

        # Game performance
        if current.efficiency < 5.0 and current.move_count > 10:
            suggestions.append("Low game efficiency - consider tuning strategy weights")

        if not suggestions:
            suggestions.append("Performance looks good! No optimizations needed.")

        return {"suggestions": suggestions, "current_metrics": asdict(current)}

# Integration with Complete2048Bot
class PerformanceIntegration:
    """Helper class to integrate performance monitoring with the bot"""

    def __init__(self, bot, monitor: PerformanceMonitor):
        self.bot = bot
        self.monitor = monitor

    def timed_operation(self, operation_name: str):
        """Decorator for timing bot operations"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Update relevant timing metric
                if operation_name == "screenshot":
                    self.monitor.update_bot_metrics(screenshot_time=duration)
                elif operation_name == "analysis":
                    self.monitor.update_bot_metrics(analysis_time=duration)
                elif operation_name == "strategy":
                    self.monitor.update_bot_metrics(strategy_time=duration)

                return result
            return wrapper
        return decorator

# Example usage and testing
if __name__ == "__main__":
    # Demo performance monitoring
    print("🚀 Performance Monitor Demo")

    monitor = PerformanceMonitor(log_interval=2.0, enable_alerts=True)

    # Add custom alert handler
    def custom_alert(message, metrics):
        print(f"🚨 ALERT: {message}")

    monitor.add_alert_callback(custom_alert)

    # Start monitoring
    monitor.start_monitoring()

    try:
        # Simulate some work
        for i in range(10):
            time.sleep(1)
            monitor.update_bot_metrics(
                move_count=i,
                game_score=i * 50,
                screenshot_time=0.1 + i * 0.05,
                analysis_time=0.05 + i * 0.02,
                strategy_time=0.02 + i * 0.01
            )

        # Generate report
        print("\n📊 Performance Report:")
        report = monitor.get_performance_report()
        print(f"Current Memory: {report['performance_summary']['current_metrics']['memory_mb']:.1f} MB")
        print(f"Current CPU: {report['performance_summary']['current_metrics']['cpu_percent']:.1f}%")

        # Get optimization suggestions
        print("\n💡 Optimization Suggestions:")
        suggestions = monitor.optimize_settings()
        for suggestion in suggestions["suggestions"]:
            print(f"   • {suggestion}")

    finally:
        monitor.stop_monitoring()
        print("✅ Performance monitoring demo completed")