"""
Pure PyGame Vaporwave Interface
Working alternative to pygame_gui with vaporwave 1984 aesthetic
"""

import pygame
import sys
import threading
import time
from typing import Dict, Any, Optional, Callable
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from vaporwave_colors import VaporwaveColors

class VaporwaveButton:
    """Vaporwave-styled button with 1984 aesthetic"""

    def __init__(self, rect, text, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.is_hovered = False
        self.is_pressed = False

    def handle_event(self, event):
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
            self.is_pressed = False

    def draw(self, surface):
        """Draw the vaporwave button"""
        # Button colors based on state
        if self.is_pressed:
            bg_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BUTTON_BG_ACTIVE)
            border_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BORDER_GREEN)
        elif self.is_hovered:
            bg_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BUTTON_BG_HOVER)
            border_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BORDER_MAGENTA)
        else:
            bg_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BUTTON_BG_PRIMARY)
            border_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BORDER_CYAN)

        # Draw button
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Draw text
        font = pygame.font.Font(None, 24)
        text_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.TEXT_WHITE)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class VaporwaveInterface:
    """Main vaporwave interface using pure PyGame"""

    def __init__(self):
        """Initialize the vaporwave interface"""
        pygame.init()

        # Window setup
        self.width = 1200
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("JED-2048 Debug Interface - Vaporwave Edition")

        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.running = False

        # Data
        self.current_screenshot = None
        self.performance_metrics = {}
        self.bot_status = "STOPPED"

        # Thread safety
        self.data_lock = threading.Lock()

        # Setup UI components
        self._setup_buttons()

        # Background colors
        self.bg_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BG_MAIN)
        self.panel_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BG_PANEL_PRIMARY)

    def _setup_buttons(self):
        """Setup vaporwave-styled buttons"""
        self.buttons = []

        # Control buttons
        button_y = 80
        button_spacing = 60

        self.start_button = VaporwaveButton(
            (20, button_y, 150, 40),
            "START BOT",
            self._start_bot
        )
        self.buttons.append(self.start_button)

        self.pause_button = VaporwaveButton(
            (20, button_y + button_spacing, 150, 40),
            "PAUSE BOT",
            self._pause_bot
        )
        self.buttons.append(self.pause_button)

        self.stop_button = VaporwaveButton(
            (20, button_y + button_spacing * 2, 150, 40),
            "STOP BOT",
            self._stop_bot
        )
        self.buttons.append(self.stop_button)

        self.emergency_button = VaporwaveButton(
            (20, button_y + button_spacing * 3, 150, 40),
            "EMERGENCY",
            self._emergency_stop
        )
        self.buttons.append(self.emergency_button)

    def _start_bot(self):
        """Start bot callback"""
        print("🚀 Bot started!")
        self.bot_status = "RUNNING"

    def _pause_bot(self):
        """Pause bot callback"""
        print("⏸️ Bot paused!")
        self.bot_status = "PAUSED"

    def _stop_bot(self):
        """Stop bot callback"""
        print("⏹️ Bot stopped!")
        self.bot_status = "STOPPED"

    def _emergency_stop(self):
        """Emergency stop callback"""
        print("🚨 Emergency stop!")
        self.bot_status = "EMERGENCY STOP"

    def update_screenshot(self, screenshot: np.ndarray):
        """Update browser screenshot"""
        with self.data_lock:
            self.current_screenshot = screenshot.copy() if screenshot is not None else None

    def update_metrics(self, metrics: Dict[str, Any]):
        """Update performance metrics"""
        with self.data_lock:
            self.performance_metrics.update(metrics)

    def _draw_panel(self, surface, rect, title):
        """Draw a vaporwave-styled panel"""
        # Panel background
        pygame.draw.rect(surface, self.panel_color, rect)

        # Panel border with cyan glow effect
        border_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BORDER_CYAN)
        pygame.draw.rect(surface, border_color, rect, 3)

        # Title
        font = pygame.font.Font(None, 28)
        text_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.TEXT_CYAN)
        title_surface = font.render(title, True, text_color)
        surface.blit(title_surface, (rect.x + 10, rect.y + 10))

    def _draw_text(self, surface, text, pos, color=None, size=24):
        """Draw text with vaporwave styling"""
        color = color or VaporwaveColors.hex_to_rgb(VaporwaveColors.TEXT_CYAN)
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, pos)

    def _render_browser_display(self):
        """Render browser screenshot in the display area"""
        if self.current_screenshot is None:
            # Draw placeholder text when no screenshot
            display_rect = pygame.Rect(420, 60, 760, 520)
            font = pygame.font.Font(None, 36)
            text_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.TEXT_CYAN)
            text = "WAITING FOR BROWSER..."
            text_surface = font.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=display_rect.center)
            self.screen.blit(text_surface, text_rect)
            return

        try:
            # Debug print to see what we're getting
            print(f"📸 Screenshot shape: {self.current_screenshot.shape}, dtype: {self.current_screenshot.dtype}")

            # Convert numpy array to pygame surface
            if len(self.current_screenshot.shape) == 3 and self.current_screenshot.shape[2] == 3:
                # Ensure RGB format and proper data type
                screenshot_rgb = self.current_screenshot.astype(np.uint8)

                # Create pygame surface from array (pygame uses different axis order)
                screenshot_surface = pygame.surfarray.make_surface(screenshot_rgb.swapaxes(0, 1))

                # Scale to fit display area
                display_rect = pygame.Rect(420, 60, 760, 520)
                scaled_surface = pygame.transform.scale(screenshot_surface,
                                                      (display_rect.width, display_rect.height))
                self.screen.blit(scaled_surface, display_rect.topleft)

                # Add border around screenshot
                border_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.BORDER_GREEN)
                pygame.draw.rect(self.screen, border_color, display_rect, 2)

            else:
                print(f"⚠️ Unexpected screenshot format: {self.current_screenshot.shape}")

        except Exception as e:
            print(f"❌ Error rendering screenshot: {e}")
            # Draw error message
            display_rect = pygame.Rect(420, 60, 760, 520)
            font = pygame.font.Font(None, 24)
            text_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.TEXT_RED)
            text = f"DISPLAY ERROR: {str(e)}"
            text_surface = font.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=display_rect.center)
            self.screen.blit(text_surface, text_rect)

    def run(self):
        """Main interface loop"""
        self.running = True

        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # Handle button events
                for button in self.buttons:
                    button.handle_event(event)

            # Clear screen
            self.screen.fill(self.bg_color)

            # Draw panels
            # Control panel
            control_rect = pygame.Rect(10, 10, 380, 780)
            self._draw_panel(self.screen, control_rect, "⚡ BOT CONTROLS")

            # Browser display panel
            browser_rect = pygame.Rect(410, 10, 780, 590)
            self._draw_panel(self.screen, browser_rect, "🖥️ BROWSER DISPLAY")

            # Metrics panel
            metrics_rect = pygame.Rect(410, 610, 780, 180)
            self._draw_panel(self.screen, metrics_rect, "📊 PERFORMANCE METRICS")

            # Draw status
            status_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.TEXT_GREEN)
            if self.bot_status == "STOPPED":
                status_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.TEXT_RED)
            elif self.bot_status == "PAUSED":
                status_color = VaporwaveColors.hex_to_rgb(VaporwaveColors.TEXT_YELLOW)

            self._draw_text(self.screen, f"STATUS: {self.bot_status}", (30, 50), status_color, 20)

            # Draw buttons
            for button in self.buttons:
                button.draw(self.screen)

            # Render browser screenshot
            with self.data_lock:
                if self.current_screenshot is not None:
                    self._render_browser_display()

            # Draw performance metrics
            y_offset = 650
            with self.data_lock:
                for key, value in self.performance_metrics.items():
                    text = f"{key.upper()}: {value}"
                    self._draw_text(self.screen, text, (420, y_offset), size=18)
                    y_offset += 25

            # Update display
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS

        pygame.quit()

def main():
    """Test the vaporwave interface"""
    print("🌸 JED-2048 Vaporwave Interface Test")

    interface = VaporwaveInterface()

    # Add some test metrics
    interface.update_metrics({
        'score': 2048,
        'moves': 125,
        'efficiency': 16.38,
        'fps': 30
    })

    # Run interface
    interface.run()

if __name__ == "__main__":
    main()