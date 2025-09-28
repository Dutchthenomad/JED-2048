"""
Performance Metrics Display
Real-time visualization of bot performance data
"""

import pygame
from typing import Dict, Any, List, Tuple
from collections import deque
import time

class MetricsDisplay:
    """
    Performance metrics visualization panel

    Displays real-time performance data, statistics, and trends
    """

    def __init__(self, config, rect: pygame.Rect):
        self.config = config
        self.rect = rect

        # Metrics data
        self.current_metrics: Dict[str, Any] = {}
        self.metric_history: Dict[str, deque] = {}
        self.max_history_length = 100

        # Display settings
        self.graph_rect = pygame.Rect(
            self.rect.x + 20,
            self.rect.y + 120,
            self.rect.width - 40,
            80
        )

    def update_metrics(self, metrics: Dict[str, Any]):
        """Update performance metrics"""
        self.current_metrics.update(metrics)

        # Add to history for trend visualization
        current_time = time.time()
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if key not in self.metric_history:
                    self.metric_history[key] = deque(maxlen=self.max_history_length)
                self.metric_history[key].append((current_time, value))

    def render(self, surface: pygame.Surface):
        """Render the metrics display"""
        # Draw panel background
        pygame.draw.rect(surface, self.config.panel_color, self.rect)
        pygame.draw.rect(surface, self.config.accent_color, self.rect, 2)

        # Draw title
        self._draw_text(surface, "Performance Metrics",
                       (self.rect.x + 20, self.rect.y + 20),
                       font_size=self.config.font_size_large)

        # Draw current metrics
        self._draw_current_metrics(surface)

        # Draw trend graph
        self._draw_trend_graph(surface)

    def _draw_current_metrics(self, surface: pygame.Surface):
        """Draw current metric values"""
        y_offset = 60
        line_height = 25

        # Key metrics to display
        display_metrics = [
            ("Score", "current_score", 0),
            ("Moves", "move_count", 0),
            ("Efficiency", "efficiency", 2),
            ("Highest Tile", "highest_tile", 0),
            ("FPS", "gui_fps", 1)
        ]

        for label, key, decimals in display_metrics:
            value = self.current_metrics.get(key, 0)

            if decimals > 0:
                value_text = f"{value:.{decimals}f}"
            else:
                value_text = str(int(value))

            text = f"{label}: {value_text}"
            self._draw_text(surface, text,
                           (self.rect.x + 20, self.rect.y + y_offset))
            y_offset += line_height

    def _draw_trend_graph(self, surface: pygame.Surface):
        """Draw simple trend graph for efficiency"""
        if "efficiency" not in self.metric_history:
            return

        history = list(self.metric_history["efficiency"])
        if len(history) < 2:
            return

        # Draw graph background
        pygame.draw.rect(surface, (20, 20, 20), self.graph_rect)
        pygame.draw.rect(surface, self.config.text_color, self.graph_rect, 1)

        # Calculate scaling
        values = [point[1] for point in history]
        min_val = min(values)
        max_val = max(values)

        if max_val - min_val == 0:
            return

        # Draw trend line
        points = []
        for i, (timestamp, value) in enumerate(history):
            x = self.graph_rect.x + (i / len(history)) * self.graph_rect.width
            y = self.graph_rect.bottom - ((value - min_val) / (max_val - min_val)) * self.graph_rect.height
            points.append((x, y))

        if len(points) > 1:
            pygame.draw.lines(surface, self.config.success_color, False, points, 2)

        # Draw graph labels
        self._draw_text(surface, f"Efficiency Trend (Min: {min_val:.2f}, Max: {max_val:.2f})",
                       (self.graph_rect.x, self.graph_rect.y - 20),
                       font_size=self.config.font_size_small)

    def _draw_text(self, surface: pygame.Surface, text: str, pos: tuple,
                   color: tuple = None, font_size: int = None):
        """Draw text helper"""
        color = color or self.config.text_color
        font_size = font_size or self.config.font_size_normal

        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, pos)

    def clear_history(self):
        """Clear metric history"""
        self.metric_history.clear()

    def get_latest_metric(self, key: str) -> Any:
        """Get latest value for a specific metric"""
        return self.current_metrics.get(key, None)