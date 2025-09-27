"""
Browser Controller for 2048 Bot (Playwright-backed)
Maintains the original BrowserController API while delegating to Playwright.
"""

import time
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from enum import Enum

import cv2
import numpy as np

from .playwright_controller import PlaywrightController


class BrowserType(Enum):
    """Supported browser types (mapped to Playwright engines)"""
    FIREFOX = "firefox"
    CHROME = "chrome"  # mapped to Playwright's chromium


class GameAction(Enum):
    """Available game actions (Playwright key names)"""
    UP = "ArrowUp"
    DOWN = "ArrowDown"
    LEFT = "ArrowLeft"
    RIGHT = "ArrowRight"
    NEW_GAME = "new_game"
    PLAY_AGAIN = "play_again"


class BrowserController:
    """
    Browser automation controller for 2048 game (Playwright-backed)
    Handles browser setup, game navigation, and input simulation.
    """

    def __init__(self, browser_type: BrowserType = BrowserType.FIREFOX, headless: bool = False):
        self.browser_type = browser_type
        self.headless = headless
        self.logger = logging.getLogger(__name__)

        # Playwright controller
        pw_browser = "firefox" if browser_type == BrowserType.FIREFOX else "chromium"
        self._controller: Optional[PlaywrightController] = PlaywrightController(
            headless=headless, browser_type=pw_browser, block_ads=True
        )

        # Game state tracking
        self.game_url: Optional[str] = None
        self.game_active = False
        self.last_action_time = 0.0

        # Timing configuration
        self.action_delay = 0.5  # Delay between actions
        self.screenshot_delay = 0.3  # Delay after actions before screenshot

    def start_browser(self) -> bool:
        """Initialize Playwright (noop until connect)."""
        try:
            # PlaywrightController connects on navigate; nothing to pre-start here
            self.logger.info(f"Browser {self.browser_type.value} ready (Playwright)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to prepare browser: {e}")
            return False

    def navigate_to_game(self, url: str) -> bool:
        """Navigate to game URL using Playwright controller."""
        try:
            self.logger.info(f"Navigating to: {url}")
            ok = self._controller.connect(url)
            if ok:
                self.game_url = url
                self.game_active = True
                self.logger.info("Successfully connected to game (Playwright)")
            return ok
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            return False

    def _focus_game_area(self) -> None:
        """No-op; Playwright focuses page by default."""
        return

    def send_game_action(self, action: GameAction) -> bool:
        """Send game action using Playwright controller."""
        if not self.game_active:
            self.logger.error("Browser not ready or game not active")
            return False

        try:
            # Respect action timing
            current_time = time.time()
            time_since_last = current_time - self.last_action_time
            if time_since_last < self.action_delay:
                time.sleep(self.action_delay - time_since_last)

            ok = True
            if action in [GameAction.UP, GameAction.DOWN, GameAction.LEFT, GameAction.RIGHT]:
                ok = self._controller.send_key(action.value)
            elif action in [GameAction.NEW_GAME, GameAction.PLAY_AGAIN]:
                ok = self._controller.reset_game()

            self.last_action_time = time.time()
            time.sleep(self.screenshot_delay)
            return bool(ok)

        except Exception as e:
            self.logger.error(f"Failed to send action {action.name}: {e}")
            return False

    # Button utilities not needed with Playwright adapter
    def _click_button(self, button_identifiers: list) -> bool:  # compatibility stub
        return False

    def take_screenshot(self, save_path: Optional[Path] = None) -> Optional[bytes]:
        """Take screenshot and return PNG bytes (for compatibility)."""
        try:
            img = self._controller.take_screenshot(str(save_path) if save_path else None)
            if img is None:
                return None
            # Ensure we have a numpy array to encode
            if isinstance(img, np.ndarray):
                success, buf = cv2.imencode('.png', img)
                if not success:
                    return None
                return buf.tobytes()
            # Fallback: if controller saved to disk only, read bytes
            if save_path and Path(save_path).exists():
                return Path(save_path).read_bytes()
            return None
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return None

    def check_game_state(self) -> Dict[str, Any]:
        """Check current game state using Playwright controller."""
        state = {
            'game_active': self.game_active,
            'game_over': False,
            'score': None,
            'new_game_available': True,   # Game typically has restart button available
            'play_again_available': False
        }
        try:
            info = self._controller.get_game_info() or {}
            state['game_over'] = bool(info.get('game_over', False))
            if 'score' in info:
                state['score'] = info['score']
            # If game over, play-again button is likely available
            state['play_again_available'] = state['game_over']
        except Exception as e:
            self.logger.warning(f"Error checking game state: {e}")
        return state

    def _button_exists(self, button_identifiers: list) -> bool:  # compatibility stub
        return False

    def close_browser(self) -> None:
        """Close browser and cleanup"""
        try:
            if self._controller:
                self._controller.cleanup()
        finally:
            self.game_active = False

    def __enter__(self):
        """Context manager entry"""
        self.start_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()

