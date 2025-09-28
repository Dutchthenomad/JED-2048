"""
Computer Vision Overlay
Real-time visualization of CV processing pipeline
"""

import pygame
import numpy as np
import cv2
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

@dataclass
class CVVisualizationData:
    """Data structure for CV visualization"""
    board_region: Optional[Tuple[int, int, int, int]] = None
    tile_positions: List[Tuple[int, int, int, int]] = None
    detected_tiles: Dict[Tuple[int, int], int] = None
    confidence_scores: Dict[Tuple[int, int], float] = None
    processing_time: float = 0.0

class ComputerVisionOverlay:
    """
    Computer vision processing visualization

    Overlays CV detection results on the browser screenshot
    """

    def __init__(self, config):
        self.config = config

    def render_overlay(self, surface: pygame.Surface, screenshot: np.ndarray,
                      cv_data: CVVisualizationData) -> pygame.Surface:
        """
        Render CV overlay on screenshot

        Args:
            surface: Target pygame surface
            screenshot: Original browser screenshot
            cv_data: Computer vision analysis data

        Returns:
            Surface with overlay rendered
        """
        if screenshot is None or cv_data is None:
            return surface

        # Create overlay surface
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)

        # Draw board region outline
        if cv_data.board_region:
            self._draw_board_outline(overlay, cv_data.board_region)

        # Draw tile detection boxes
        if cv_data.tile_positions:
            self._draw_tile_boxes(overlay, cv_data.tile_positions, cv_data.detected_tiles)

        # Draw confidence indicators
        if cv_data.confidence_scores:
            self._draw_confidence_indicators(overlay, cv_data.confidence_scores)

        # Blend overlay with main surface
        surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

        return surface

    def _draw_board_outline(self, surface: pygame.Surface, board_region: Tuple[int, int, int, int]):
        """Draw outline around detected board region"""
        x, y, w, h = board_region
        color = self.config.accent_color + (int(255 * self.config.cv_overlay_opacity),)

        # Draw board boundary
        pygame.draw.rect(surface, color, (x, y, w, h), self.config.board_outline_thickness)

    def _draw_tile_boxes(self, surface: pygame.Surface, tile_positions: List,
                        detected_tiles: Dict):
        """Draw boxes around detected tiles with values"""
        for i, (x, y, w, h) in enumerate(tile_positions):
            row, col = divmod(i, 4)

            # Get tile value
            tile_value = detected_tiles.get((row, col), 0) if detected_tiles else 0

            # Choose color based on tile value
            if tile_value == 0:
                color = self.config.text_color
            elif tile_value <= 16:
                color = self.config.success_color
            elif tile_value <= 128:
                color = self.config.warning_color
            else:
                color = self.config.error_color

            # Add alpha
            color = color + (int(255 * self.config.cv_overlay_opacity),)

            # Draw tile outline
            pygame.draw.rect(surface, color, (x, y, w, h), self.config.tile_outline_thickness)

            # Draw tile value
            if tile_value > 0:
                font = pygame.font.Font(None, self.config.font_size_small)
                text = font.render(str(tile_value), True, color)
                text_rect = text.get_rect(center=(x + w//2, y + h//2))
                surface.blit(text, text_rect)

    def _draw_confidence_indicators(self, surface: pygame.Surface,
                                  confidence_scores: Dict[Tuple[int, int], float]):
        """Draw confidence level indicators"""
        # TODO: Implement confidence visualization
        pass

    def create_processing_visualization(self, original_image: np.ndarray,
                                      processing_steps: Dict[str, np.ndarray]) -> pygame.Surface:
        """Create side-by-side processing step visualization"""
        # TODO: Implement in Phase 2
        pass