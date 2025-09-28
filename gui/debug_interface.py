"""Vaporwave debug interface powered by pygame_gui.

Provides a threaded UI wrapper used by GUIEnhanced2048Bot. The interface is
responsible for rendering the live browser feed, visual overlays from the vision
system, performance metrics, and interactive controls.
"""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pygame

# Compatibility shims for pygame_gui when running on pygame < 2.6
if not hasattr(pygame, "DIRECTION_LTR"):
    pygame.DIRECTION_LTR = 0
    pygame.DIRECTION_RTL = 1

if not hasattr(pygame, "FRect"):
    try:
        pygame.FRect = pygame.Rect
    except AttributeError:
        # Fallback for pygame-ce compatibility
        import pygame_ce
        pygame.FRect = getattr(pygame_ce, 'FRect', pygame_ce.Rect)

import pygame_gui

from .gui_config import GUIConfig
from .vaporwave_colors import VaporwaveColors, VaporwaveLayout


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert a hex colour string (#RRGGBB) into an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


class _ControlBindings:
    """Proxy object that mirrors the original control_panel API."""

    def __init__(self, parent: 'DebugInterface') -> None:
        self._parent = parent

    def register_callback(self, action: str, callback: Callable[[], None]) -> None:
        self._parent.register_action(action, callback)

    def update_bot_state(self, state) -> None:  # type: ignore[override]
        self._parent.queue_status_update(state)


class DebugInterface:
    """Threaded vaporwave GUI built on top of pygame_gui."""

    def __init__(self, config: Optional[GUIConfig] = None) -> None:
        self.config = config or GUIConfig()

        # Runtime objects initialised in _run_loop
        self.screen: Optional[pygame.Surface] = None
        self.ui_manager: Optional[pygame_gui.UIManager] = None
        self.clock: Optional[pygame.time.Clock] = None

        # UI element handles populated during setup
        self.status_label: Optional[pygame_gui.elements.UILabel] = None
        self.score_label: Optional[pygame_gui.elements.UILabel] = None
        self.moves_progress: Optional[pygame_gui.elements.UIProgressBar] = None
        self.accuracy_label: Optional[pygame_gui.elements.UILabel] = None
        self.vision_label: Optional[pygame_gui.elements.UILabel] = None
        self.next_move_label: Optional[pygame_gui.elements.UILabel] = None
        self.reasoning_text: Optional[pygame_gui.elements.UITextBox] = None
        self.fps_label: Optional[pygame_gui.elements.UILabel] = None

        self.start_button = None
        self.pause_button = None
        self.stop_button = None
        self.emergency_button = None
        self.step_button = None
        self.algorithm_dropdown = None
        self.speed_slider = None
        self.zoom_slider = None
        self.view_raw_button = None
        self.view_proc_button = None
        self.save_debug_button = None
        self.screenshot_button = None
        self.record_button = None
        self.game_area_panel = None
        self.tile_detection_toggle = None
        self.boundary_toggle = None
        self.preview_toggle = None
        self.heatmap_toggle = None

        # Absolute rects used when blitting the screenshot/overlays
        self.game_area_rect = pygame.Rect(
            VaporwaveLayout.CONTROL_PANEL_WIDTH + VaporwaveLayout.PANEL_MARGIN,
            VaporwaveLayout.PANEL_MARGIN,
            VaporwaveLayout.GAME_AREA_WIDTH,
            VaporwaveLayout.GAME_AREA_HEIGHT,
        )

        # State shared between bot thread and GUI thread
        self._lock = threading.Lock()
        self._latest_frame: Optional[np.ndarray] = None
        self._screenshot_surface: Optional[pygame.Surface] = None
        self._cv_overlay: Dict[str, Any] = {}
        self._board_state: Optional[List[List[int]]] = None
        self._metrics: Dict[str, Any] = {}
        self._strategy: Dict[str, Any] = {}
        self._pending_status: Optional[Tuple[str, str]] = None

        self.overlay_states: Dict[str, bool] = {
            'tile_detection': True,
            'boundaries': False,
            'preview': True,
            'heatmap': False,
        }

        self._action_handlers: Dict[str, Callable[[], None]] = {}
        self.control_panel = _ControlBindings(self)
        self._bot_instance = None

        # Thread lifecycle
        self._thread: Optional[threading.Thread] = None
        self._running = False

    # ------------------------------------------------------------------
    # Public API used by GUIEnhanced2048Bot
    # ------------------------------------------------------------------
    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def register_bot(self, bot_instance: Any) -> None:
        self._bot_instance = bot_instance

    def register_action(self, action: str, callback: Callable[[], None]) -> None:
        self._action_handlers[action] = callback

    def queue_status_update(self, state: Any) -> None:
        """Accept BotState updates from the bot thread."""
        label_text, object_id = self._status_text_from_state(state)
        with self._lock:
            self._pending_status = (label_text, object_id)

    def update_screenshot(self, frame: np.ndarray) -> None:
        with self._lock:
            self._latest_frame = None if frame is None else frame.copy()
            self._screenshot_surface = None  # force regeneration with new size

    def update_board_state(self, board_state: List[List[int]]) -> None:
        with self._lock:
            self._board_state = [row[:] for row in board_state] if board_state else None

    def update_cv_analysis(self, analysis_data: Dict[str, Any]) -> None:
        with self._lock:
            self._cv_overlay = analysis_data.copy() if analysis_data else {}

    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        with self._lock:
            self._metrics.update(metrics)

    def update_strategy_info(self, next_move: Optional[str] = None,
                             confidence: Optional[float] = None,
                             reasoning: Optional[str] = None) -> None:
        with self._lock:
            if next_move is not None:
                self._strategy['next_move'] = next_move
            if confidence is not None:
                self._strategy['confidence'] = confidence
            if reasoning is not None:
                self._strategy['reasoning'] = reasoning

    def draw_game_display(self, screenshot: np.ndarray) -> None:
        """Backwards-compatible alias for update_screenshot."""
        self.update_screenshot(screenshot)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run_loop(self) -> None:
        """Main pygame event/render loop run on a background thread."""
        pygame.init()
        window_size = (VaporwaveLayout.WINDOW_WIDTH, VaporwaveLayout.WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("JED-2048 Bot Interface - Vaporwave Edition")

        theme_path = Path(__file__).parent / "vaporwave_theme.json"
        if theme_path.exists():
            self.ui_manager = pygame_gui.UIManager(window_size, str(theme_path))
        else:
            self.ui_manager = pygame_gui.UIManager(window_size)

        self.clock = pygame.time.Clock()
        self._build_layout()

        while self._running:
            time_delta = self.clock.tick(self.config.fps) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    break
                self._handle_events(event)
                if self.ui_manager:
                    self.ui_manager.process_events(event)

            self._apply_pending_updates()
            if self.ui_manager:
                self.ui_manager.update(time_delta)

            self._render_frame()

        pygame.quit()
        self.screen = None
        self.ui_manager = None
        self.clock = None

    def _build_layout(self) -> None:
        self._setup_control_panel()
        self._setup_browser_display()

    def _setup_control_panel(self) -> None:
        ui = self.ui_manager
        if ui is None:
            return

        panel_x = VaporwaveLayout.PANEL_MARGIN
        current_y = VaporwaveLayout.PANEL_MARGIN
        panel_width = VaporwaveLayout.CONTROL_PANEL_WIDTH - (VaporwaveLayout.PANEL_MARGIN * 2)

        # Status panel --------------------------------------------------
        status_height = 80
        status_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, current_y, panel_width, status_height),
            manager=ui
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 5, panel_width - 10, 20),
            text="⚡ BOT STATUS",
            manager=ui,
            container=status_panel,
            object_id="#panel_title"
        )
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 25, panel_width - 10, 20),
            text="STATUS: ●STOPPED",
            manager=ui,
            container=status_panel,
            object_id="#status_stopped"
        )
        self.emergency_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(5, 45, panel_width - 10, 25),
            text="⚠ EMERGENCY HALT ⚠",
            manager=ui,
            container=status_panel,
            object_id="#emergency_button"
        )
        current_y += status_height + 15

        # Controls panel -----------------------------------------------
        controls_height = 280
        controls_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, current_y, panel_width, controls_height),
            manager=ui
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 5, panel_width - 10, 20),
            text="🎮 CONTROLS",
            manager=ui,
            container=controls_panel,
            object_id="#panel_title"
        )
        button_width = (panel_width - 25) // 4
        button_y = 25
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(5, button_y, button_width, VaporwaveLayout.BUTTON_HEIGHT),
            text="START",
            manager=ui,
            container=controls_panel
        )
        self.pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + button_width, button_y, button_width, VaporwaveLayout.BUTTON_HEIGHT),
            text="PAUSE",
            manager=ui,
            container=controls_panel
        )
        self.stop_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(15 + button_width * 2, button_y, button_width, VaporwaveLayout.BUTTON_HEIGHT),
            text="STOP",
            manager=ui,
            container=controls_panel
        )
        self.step_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(20 + button_width * 3, button_y, button_width, VaporwaveLayout.BUTTON_HEIGHT),
            text="STEP",
            manager=ui,
            container=controls_panel
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 65, panel_width - 10, 15),
            text="ALGORITHM:",
            manager=ui,
            container=controls_panel
        )
        self.algorithm_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(5, 80, panel_width - 10, VaporwaveLayout.DROPDOWN_HEIGHT),
            options_list=["ENHANCED_HEURISTIC", "BASIC_PRIORITY", "RANDOM_WALKER"],
            starting_option="ENHANCED_HEURISTIC",
            manager=ui,
            container=controls_panel
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 110, panel_width - 10, 15),
            text="SPEED:",
            manager=ui,
            container=controls_panel
        )
        self.speed_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(5, 125, panel_width - 10, VaporwaveLayout.SLIDER_HEIGHT),
            start_value=50,
            value_range=(1, 100),
            manager=ui,
            container=controls_panel
        )
        current_y += controls_height + 15

        # Metrics panel ------------------------------------------------
        metrics_height = 120
        metrics_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, current_y, panel_width, metrics_height),
            manager=ui
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 5, panel_width - 10, 20),
            text="📊 PERFORMANCE",
            manager=ui,
            container=metrics_panel,
            object_id="#panel_title"
        )
        self.score_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 25, panel_width - 10, 15),
            text="SCORE: 0",
            manager=ui,
            container=metrics_panel,
            object_id="#metric_value"
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 45, panel_width - 10, 15),
            text="MOVES/SEC:",
            manager=ui,
            container=metrics_panel
        )
        self.moves_progress = pygame_gui.elements.UIProgressBar(
            relative_rect=pygame.Rect(5, 60, panel_width - 10, VaporwaveLayout.PROGRESS_HEIGHT),
            manager=ui,
            container=metrics_panel
        )
        self.accuracy_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 85, panel_width - 10, 15),
            text="ACCURACY: --",
            manager=ui,
            container=metrics_panel,
            object_id="#metric_value"
        )
        self.vision_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 100, panel_width - 10, 15),
            text="VISION: --",
            manager=ui,
            container=metrics_panel,
            object_id="#metric_value"
        )
        current_y += metrics_height + 15

        # Strategy panel ----------------------------------------------
        strategy_height = 100
        strategy_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, current_y, panel_width, strategy_height),
            manager=ui
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 5, panel_width - 10, 20),
            text="🧠 STRATEGY",
            manager=ui,
            container=strategy_panel,
            object_id="#panel_title"
        )
        self.next_move_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 25, panel_width - 10, 15),
            text="NEXT: --",
            manager=ui,
            container=strategy_panel,
            object_id="#metric_value"
        )
        self.reasoning_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(5, 45, panel_width - 10, 50),
            html_text="Strategy reasoning will appear here.",
            manager=ui,
            container=strategy_panel
        )
        current_y += strategy_height + 15

        # CV Debug panel ----------------------------------------------
        debug_height = 100
        debug_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(panel_x, current_y, panel_width, debug_height),
            manager=ui
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 5, panel_width - 10, 20),
            text="👁 CV DEBUG",
            manager=ui,
            container=debug_panel,
            object_id="#panel_title"
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(5, 25, panel_width - 10, 15),
            text="PIPELINE: READY",
            manager=ui,
            container=debug_panel,
            object_id="#metric_value"
        )
        debug_button_width = (panel_width - 20) // 3
        self.view_raw_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(5, 45, debug_button_width, 25),
            text="RAW",
            manager=ui,
            container=debug_panel
        )
        self.view_proc_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10 + debug_button_width, 45, debug_button_width, 25),
            text="PROC",
            manager=ui,
            container=debug_panel
        )
        self.save_debug_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(15 + debug_button_width * 2, 45, debug_button_width, 25),
            text="SAVE",
            manager=ui,
            container=debug_panel
        )

    def _setup_browser_display(self) -> None:
        ui = self.ui_manager
        if ui is None:
            return

        browser_x = VaporwaveLayout.CONTROL_PANEL_WIDTH + VaporwaveLayout.PANEL_MARGIN
        overlay_y = VaporwaveLayout.PANEL_MARGIN + VaporwaveLayout.GAME_AREA_HEIGHT + 10
        overlay_width = VaporwaveLayout.GAME_AREA_WIDTH

        self.game_area_panel = pygame_gui.elements.UIPanel(
            relative_rect=self.game_area_rect,
            manager=ui,
            object_id="#game_area"
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(
                VaporwaveLayout.GAME_AREA_WIDTH // 2 - 150,
                VaporwaveLayout.GAME_AREA_HEIGHT // 2 - 20,
                300,
                40,
            ),
            text="🎮 LIVE GAME DISPLAY",
            manager=ui,
            container=self.game_area_panel,
            object_id="#panel_title"
        )

        overlay_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(
                browser_x,
                overlay_y,
                overlay_width,
                VaporwaveLayout.OVERLAY_PANEL_HEIGHT,
            ),
            manager=ui,
            object_id="#overlay_panel"
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 5, overlay_width - 20, 20),
            text="◈ COMPUTER VISION OVERLAYS ◈",
            manager=ui,
            container=overlay_panel,
            object_id="#panel_title"
        )
        checkbox_y = 30
        checkbox_width = 150
        self.tile_detection_toggle = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, checkbox_y, checkbox_width, 25),
            text="☑ TILE DETECTION",
            manager=ui,
            container=overlay_panel
        )
        self.boundary_toggle = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(170, checkbox_y, checkbox_width, 25),
            text="☐ BOUNDARIES",
            manager=ui,
            container=overlay_panel
        )
        self.preview_toggle = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(330, checkbox_y, checkbox_width, 25),
            text="☑ MOVE PREVIEW",
            manager=ui,
            container=overlay_panel
        )
        self.heatmap_toggle = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(490, checkbox_y, checkbox_width, 25),
            text="☐ HEATMAP",
            manager=ui,
            container=overlay_panel
        )
        controls_y = 65
        self.screenshot_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, controls_y, 100, 25),
            text="📷 CAPTURE",
            manager=ui,
            container=overlay_panel
        )
        self.record_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(120, controls_y, 100, 25),
            text="🔴 RECORD",
            manager=ui,
            container=overlay_panel
        )
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(240, controls_y, 50, 25),
            text="ZOOM:",
            manager=ui,
            container=overlay_panel
        )
        self.zoom_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(300, controls_y + 2, 150, 20),
            start_value=100,
            value_range=(50, 200),
            manager=ui,
            container=overlay_panel
        )
        self.fps_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(470, controls_y, 100, 25),
            text="FPS: 0",
            manager=ui,
            container=overlay_panel,
            object_id="#metric_value"
        )

    def _handle_events(self, event: pygame.event.Event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_button:
                self._fire_action('start')
            elif event.ui_element == self.pause_button:
                self._fire_action('pause')
            elif event.ui_element == self.stop_button:
                self._fire_action('stop')
            elif event.ui_element == self.step_button:
                self._fire_action('step')
            elif event.ui_element == self.emergency_button:
                self._fire_action('emergency_stop')
            elif event.ui_element == self.tile_detection_toggle:
                self._toggle_overlay('tile_detection', event.ui_element)
            elif event.ui_element == self.boundary_toggle:
                self._toggle_overlay('boundaries', event.ui_element)
            elif event.ui_element == self.preview_toggle:
                self._toggle_overlay('preview', event.ui_element)
            elif event.ui_element == self.heatmap_toggle:
                self._toggle_overlay('heatmap', event.ui_element)
            elif event.ui_element == self.screenshot_button:
                self._fire_action('capture_screenshot')
            elif event.ui_element == self.record_button:
                self._toggle_record(event.ui_element)
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.algorithm_dropdown:
                self._fire_action('change_algorithm', event.text)
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            if event.ui_element == self.speed_slider:
                self._fire_action('speed_changed', event.value)
            elif event.ui_element == self.zoom_slider:
                self._fire_action('zoom_changed', event.value)

    def _fire_action(self, action: str, *args) -> None:
        callback = self._action_handlers.get(action)
        if callback:
            try:
                if args:
                    callback(*args)  # type: ignore[misc]
                else:
                    callback()
            except Exception as exc:
                print(f"GUI action '{action}' failed: {exc}")

    def _toggle_overlay(self, key: str, button: pygame_gui.elements.UIButton) -> None:
        self.overlay_states[key] = not self.overlay_states.get(key, False)
        prefix = "☑" if self.overlay_states[key] else "☐"
        label = button.text.split(' ', 1)[-1]
        button.set_text(f"{prefix} {label}")

    def _toggle_record(self, button: pygame_gui.elements.UIButton) -> None:
        is_recording = button.text.startswith('🔴')
        if is_recording:
            button.set_text("⏹ STOP REC")
            self._fire_action('start_recording')
        else:
            button.set_text("🔴 RECORD")
            self._fire_action('stop_recording')

    def _apply_pending_updates(self) -> None:
        with self._lock:
            metrics = self._metrics.copy()
            strategy = self._strategy.copy()
            pending_status = self._pending_status
            self._pending_status = None

        if pending_status and self.status_label:
            text, object_id = pending_status
            self.status_label.set_text(text)
            self.status_label.set_object_id(object_id, 'label')

        if metrics:
            self._update_metrics_ui(metrics)
        if strategy:
            self._update_strategy_ui(strategy)

    def _update_metrics_ui(self, metrics: Dict[str, Any]) -> None:
        if self.score_label and 'current_score' in metrics:
            self.score_label.set_text(f"SCORE: {int(metrics['current_score'])}")
        if self.moves_progress:
            moves_per_sec = metrics.get('moves_per_second') or metrics.get('moves_per_sec') or 0
            progress_value = max(0.0, min(100.0, float(moves_per_sec) * 10.0))
            self.moves_progress.set_current_progress(progress_value)
        if self.accuracy_label and 'accuracy' in metrics:
            self.accuracy_label.set_text(f"ACCURACY: {metrics['accuracy']:.0f}%")
        if self.vision_label and 'vision_time' in metrics:
            self.vision_label.set_text(f"VISION: {metrics['vision_time']:.1f}ms")
        if self.fps_label and 'gui_fps' in metrics:
            self.fps_label.set_text(f"FPS: {metrics['gui_fps']:.1f}")

    def _update_strategy_ui(self, strategy: Dict[str, Any]) -> None:
        if self.next_move_label and 'next_move' in strategy:
            confidence = strategy.get('confidence')
            if confidence is not None:
                self.next_move_label.set_text(f"NEXT: {strategy['next_move']} ({confidence:.0f}%)")
            else:
                self.next_move_label.set_text(f"NEXT: {strategy['next_move']}")
        if self.reasoning_text and 'reasoning' in strategy:
            self.reasoning_text.set_text(strategy['reasoning'])

    def _render_frame(self) -> None:
        if self.screen is None:
            return
        self.screen.fill(_hex_to_rgb(VaporwaveColors.BG_MAIN))
        self._render_game_display()
        if self.ui_manager:
            self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

    def _render_game_display(self) -> None:
        if self.screen is None:
            return
        with self._lock:
            frame = None if self._latest_frame is None else self._latest_frame.copy()
            cv_overlay = self._cv_overlay.copy()
        if frame is None:
            return

        if self._screenshot_surface is None or self._screenshot_surface.get_size() != (frame.shape[1], frame.shape[0]):
            surface = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), 'RGB')
            self._screenshot_surface = surface
        scaled_surface = pygame.transform.smoothscale(self._screenshot_surface, self.game_area_rect.size)
        self.screen.blit(scaled_surface, self.game_area_rect)
        self._render_overlays(cv_overlay, frame.shape[1], frame.shape[0])

    def _render_overlays(self, overlay: Dict[str, Any], width: int, height: int) -> None:
        if self.screen is None:
            return
        if not overlay:
            return

        scale_x = self.game_area_rect.width / max(width, 1)
        scale_y = self.game_area_rect.height / max(height, 1)

        def _scale_rect(rect: Tuple[int, int, int, int]) -> pygame.Rect:
            x, y, w, h = rect
            return pygame.Rect(
                self.game_area_rect.x + int(x * scale_x),
                self.game_area_rect.y + int(y * scale_y),
                max(1, int(w * scale_x)),
                max(1, int(h * scale_y)),
            )

        if self.overlay_states.get('boundaries') and overlay.get('board_region'):
            rect = _scale_rect(tuple(overlay['board_region']))
            pygame.draw.rect(self.screen, _hex_to_rgb(VaporwaveColors.BORDER_MAGENTA), rect, 3)

        if self.overlay_states.get('tile_detection') and overlay.get('tile_positions'):
            mapping = overlay.get('tile_mapping', {})
            confidences = overlay.get('confidence_map', {})
            for idx, tile in enumerate(overlay['tile_positions']):
                rect = _scale_rect(tuple(tile))
                row, col = divmod(idx, 4)
                value = mapping.get((row, col), 0)
                confidence = confidences.get((row, col), 0.0)
                color = self._tile_color(value, confidence)
                pygame.draw.rect(self.screen, color, rect, 2)

    def _tile_color(self, value: int, confidence: float) -> Tuple[int, int, int]:
        if value == 0:
            base = _hex_to_rgb(VaporwaveColors.TEXT_CYAN)
        elif value <= 64:
            base = _hex_to_rgb(VaporwaveColors.TEXT_GREEN)
        else:
            base = _hex_to_rgb(VaporwaveColors.TEXT_YELLOW)
        alpha = max(0.3, min(1.0, confidence))
        return tuple(int(channel * alpha) for channel in base)

    def _status_text_from_state(self, state: Any) -> Tuple[str, str]:
        name = getattr(state, 'value', str(state)).lower()
        mapping = {
            'running': ("STATUS: ●RUNNING", "#status_running"),
            'paused': ("STATUS: ●PAUSED", "#status_paused"),
            'stopped': ("STATUS: ●STOPPED", "#status_stopped"),
            'error': ("STATUS: ●ERROR", "#status_stopped"),
        }
        return mapping.get(name, ("STATUS: ●STOPPED", "#status_stopped"))
