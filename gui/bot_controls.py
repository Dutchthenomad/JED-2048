"""
Bot Control Panel
Interactive controls for bot operation and algorithm selection
"""

import pygame
from typing import Dict, Any, Callable, Optional, List
from enum import Enum

class BotState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

class Button:
    """Simple button widget"""

    def __init__(self, rect: pygame.Rect, text: str, callback: Callable,
                 color: tuple, text_color: tuple):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.color = color
        self.text_color = text_color
        self.enabled = True
        self.pressed = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events"""
        if not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.callback()
                self.pressed = False
                return True
            self.pressed = False

        return False

    def draw(self, surface: pygame.Surface):
        """Draw the button"""
        color = self.color if self.enabled else (100, 100, 100)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        # Draw text
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class BotControlPanel:
    """
    Bot control interface panel

    Provides buttons and controls for bot operation
    """

    def __init__(self, config, rect: pygame.Rect):
        self.config = config
        self.rect = rect
        self.bot_state = BotState.STOPPED

        # Control callbacks
        self.callbacks: Dict[str, Callable] = {}

        # UI elements
        self.buttons: List[Button] = []
        self.status_text = "Bot: Stopped"
        self.current_algorithm = "Enhanced Heuristic"
        self.available_algorithms = ["Enhanced Heuristic", "Basic Priority", "Random"]

        self._setup_controls()

    def _setup_controls(self):
        """Initialize control elements"""
        button_width = self.config.button_size[0]
        button_height = self.config.button_size[1]
        button_spacing = 10

        x = self.rect.x + 20
        y = self.rect.y + 60

        # Start/Stop button
        start_button = Button(
            pygame.Rect(x, y, button_width, button_height),
            "Start Bot",
            lambda: self._handle_start_stop(),
            self.config.success_color,
            (255, 255, 255)
        )
        self.buttons.append(start_button)

        # Pause button
        y += button_height + button_spacing
        pause_button = Button(
            pygame.Rect(x, y, button_width, button_height),
            "Pause",
            lambda: self._handle_pause(),
            self.config.warning_color,
            (255, 255, 255)
        )
        self.buttons.append(pause_button)

        # Emergency stop
        y += button_height + button_spacing
        stop_button = Button(
            pygame.Rect(x, y, button_width, button_height),
            "Emergency Stop",
            lambda: self._handle_emergency_stop(),
            self.config.error_color,
            (255, 255, 255)
        )
        self.buttons.append(stop_button)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle GUI events"""
        for button in self.buttons:
            if button.handle_event(event):
                return True
        return False

    def render(self, surface: pygame.Surface):
        """Render the control panel"""
        # Draw panel background
        pygame.draw.rect(surface, self.config.panel_color, self.rect)
        pygame.draw.rect(surface, self.config.accent_color, self.rect, 2)

        # Draw title
        self._draw_text(surface, "Bot Controls", (self.rect.x + 20, self.rect.y + 20),
                       font_size=self.config.font_size_large)

        # Draw status
        status_color = self._get_status_color()
        self._draw_text(surface, self.status_text, (self.rect.x + 20, self.rect.y + 350),
                       color=status_color)

        # Draw algorithm info
        self._draw_text(surface, f"Algorithm: {self.current_algorithm}",
                       (self.rect.x + 20, self.rect.y + 380))

        # Draw buttons
        for button in self.buttons:
            button.draw(surface)

    def register_callback(self, action: str, callback: Callable):
        """Register callback for bot actions"""
        self.callbacks[action] = callback

    def update_bot_state(self, state: BotState):
        """Update bot state"""
        self.bot_state = state
        self._update_status_text()
        self._update_button_states()

    def update_algorithm(self, algorithm_name: str):
        """Update current algorithm"""
        self.current_algorithm = algorithm_name

    def _handle_start_stop(self):
        """Handle start/stop button click"""
        if self.bot_state == BotState.STOPPED:
            if "start" in self.callbacks:
                self.callbacks["start"]()
        else:
            if "stop" in self.callbacks:
                self.callbacks["stop"]()

    def _handle_pause(self):
        """Handle pause button click"""
        if "pause" in self.callbacks:
            self.callbacks["pause"]()

    def _handle_emergency_stop(self):
        """Handle emergency stop"""
        if "emergency_stop" in self.callbacks:
            self.callbacks["emergency_stop"]()

    def _update_status_text(self):
        """Update status text based on bot state"""
        state_text = {
            BotState.STOPPED: "Bot: Stopped",
            BotState.RUNNING: "Bot: Running",
            BotState.PAUSED: "Bot: Paused",
            BotState.ERROR: "Bot: Error"
        }
        self.status_text = state_text.get(self.bot_state, "Bot: Unknown")

    def _update_button_states(self):
        """Update button states based on bot state"""
        # Update start/stop button
        if self.buttons:
            start_button = self.buttons[0]
            if self.bot_state == BotState.STOPPED:
                start_button.text = "Start Bot"
                start_button.color = self.config.success_color
            else:
                start_button.text = "Stop Bot"
                start_button.color = self.config.error_color

    def _get_status_color(self) -> tuple:
        """Get color for status text"""
        color_map = {
            BotState.STOPPED: self.config.text_color,
            BotState.RUNNING: self.config.success_color,
            BotState.PAUSED: self.config.warning_color,
            BotState.ERROR: self.config.error_color
        }
        return color_map.get(self.bot_state, self.config.text_color)

    def _draw_text(self, surface: pygame.Surface, text: str, pos: tuple,
                   color: tuple = None, font_size: int = None):
        """Draw text helper"""
        color = color or self.config.text_color
        font_size = font_size or self.config.font_size_normal

        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, pos)