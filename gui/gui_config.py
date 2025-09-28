"""
GUI Configuration Settings
Centralized configuration for the debug interface
"""

from dataclasses import dataclass
from typing import Tuple, Dict, Any

@dataclass
class GUIConfig:
    """Configuration settings for the debug GUI"""

    # Window settings
    window_size: Tuple[int, int] = (1200, 800)
    title: str = "JED-2048 Debug Interface"
    fps: int = 30

    # Layout settings
    browser_panel_size: Tuple[int, int] = (800, 600)
    control_panel_size: Tuple[int, int] = (400, 600)
    metrics_panel_height: int = 200

    # Colors (RGB)
    background_color: Tuple[int, int, int] = (40, 44, 52)
    panel_color: Tuple[int, int, int] = (33, 37, 43)
    text_color: Tuple[int, int, int] = (171, 178, 191)
    accent_color: Tuple[int, int, int] = (97, 175, 239)
    success_color: Tuple[int, int, int] = (152, 195, 121)
    warning_color: Tuple[int, int, int] = (229, 192, 123)
    error_color: Tuple[int, int, int] = (224, 108, 117)

    # Computer vision overlay settings
    cv_overlay_opacity: float = 0.7
    board_outline_thickness: int = 3
    tile_outline_thickness: int = 2
    confidence_threshold: float = 0.8

    # Font settings
    font_size_normal: int = 14
    font_size_large: int = 18
    font_size_small: int = 12

    # Performance settings
    screenshot_max_size: Tuple[int, int] = (800, 600)
    update_interval_ms: int = 33  # ~30 FPS

    # Control settings
    button_size: Tuple[int, int] = (120, 35)
    slider_length: int = 200

    @classmethod
    def load_from_file(cls, config_path: str) -> 'GUIConfig':
        """Load configuration from JSON file"""
        # TODO: Implement JSON loading in Phase 3
        return cls()

    def save_to_file(self, config_path: str):
        """Save configuration to JSON file"""
        # TODO: Implement JSON saving in Phase 3
        pass