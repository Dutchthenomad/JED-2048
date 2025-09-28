# Vaporwave Theme Colors for pygame_gui
# Based on Warakami Vaporwave "84" Series Aesthetic

class VaporwaveColors:
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    # Primary Background Colors
    BG_MAIN = "#0a0a0a"              # Main window background
    BG_PANEL_PRIMARY = "#001122"      # Primary panel backgrounds
    BG_PANEL_SECONDARY = "#000011"    # Secondary panel backgrounds
    BG_GAME_AREA = "#110022"          # Game display area background
    BG_OVERLAY_PANEL = "#001428"      # Overlay controls background

    # Border Colors
    BORDER_CYAN = "#00ffff"           # Primary borders (cyan)
    BORDER_MAGENTA = "#ff00ff"        # Secondary borders (magenta)
    BORDER_WHITE = "#ffffff"          # Button borders
    BORDER_GREEN = "#00ff00"          # Active state borders

    # Text Colors
    TEXT_CYAN = "#00ffff"             # Primary text color
    TEXT_GREEN = "#00ff00"            # Status text (running)
    TEXT_RED = "#ff0000"              # Error/stop text
    TEXT_YELLOW = "#ffff00"           # Metric values
    TEXT_WHITE = "#ffffff"            # Button text
    TEXT_BLACK = "#000000"            # Button text on bright backgrounds

    # Button Colors
    BUTTON_BG_PRIMARY = "#ff00ff"     # Primary button background
    BUTTON_BG_SECONDARY = "#00ffff"   # Secondary button background
    BUTTON_BG_EMERGENCY = "#ff0000"   # Emergency button background
    BUTTON_BG_ACTIVE = "#00ff00"      # Active button background
    BUTTON_BG_HOVER = "#00ffff"       # Button hover state

class VaporwaveColorsOriginal:
    """
    Color constants for the JED-2048 Vaporwave Interface Theme
    All colors in hex format for pygame_gui compatibility
    """
    
    # Primary Background Colors
    BG_MAIN = "#0a0a0a"              # Main window background
    BG_PANEL_PRIMARY = "#001122"      # Primary panel backgrounds
    BG_PANEL_SECONDARY = "#000011"    # Secondary panel backgrounds
    BG_GAME_AREA = "#110022"          # Game display area background
    BG_OVERLAY_PANEL = "#001428"      # Overlay controls background
    
    # Border Colors
    BORDER_CYAN = "#00ffff"           # Primary borders (cyan)
    BORDER_MAGENTA = "#ff00ff"        # Secondary borders (magenta)
    BORDER_WHITE = "#ffffff"          # Button borders
    BORDER_GREEN = "#00ff00"          # Active state borders
    
    # Text Colors
    TEXT_CYAN = "#00ffff"             # Primary text color
    TEXT_GREEN = "#00ff00"            # Status text (running)
    TEXT_RED = "#ff0000"              # Error/stop text
    TEXT_YELLOW = "#ffff00"           # Metric values
    TEXT_WHITE = "#ffffff"            # Button text
    TEXT_BLACK = "#000000"            # Button text on bright backgrounds
    
    # Button Colors
    BUTTON_BG_PRIMARY = "#ff00ff"     # Primary button background
    BUTTON_BG_SECONDARY = "#00ffff"   # Secondary button background
    BUTTON_BG_EMERGENCY = "#ff0000"   # Emergency button background
    BUTTON_BG_ACTIVE = "#00ff00"      # Active button background
    BUTTON_BG_HOVER = "#00ffff"       # Button hover state
    
    # Progress Bar Colors
    PROGRESS_BG = "#000033"           # Progress bar background
    PROGRESS_FILL_START = "#00ff00"   # Progress bar fill start color
    PROGRESS_FILL_MID = "#ffff00"     # Progress bar fill middle color
    PROGRESS_FILL_END = "#ff00ff"     # Progress bar fill end color
    
    # Slider Colors
    SLIDER_BG = "#000033"             # Slider track background
    SLIDER_FILL = "#ff00ff"           # Slider filled portion
    SLIDER_THUMB = "#ffffff"          # Slider thumb color
    
    # Dropdown Colors
    DROPDOWN_BG = "#001133"           # Dropdown background
    DROPDOWN_TEXT = "#00ffff"         # Dropdown text
    DROPDOWN_BORDER = "#00ffff"       # Dropdown border
    
    # Text Box Colors
    TEXTBOX_BG = "#000000"            # Text box background
    TEXTBOX_TEXT = "#00ff00"          # Text box text
    TEXTBOX_BORDER = "#00ffff"        # Text box border
    
    # Glow/Shadow Colors (for pygame effects)
    GLOW_CYAN = "#00ffff"             # Cyan glow effect
    GLOW_MAGENTA = "#ff00ff"          # Magenta glow effect
    GLOW_GREEN = "#00ff00"            # Green glow effect
    GLOW_YELLOW = "#ffff00"           # Yellow glow effect
    
    # Transparency values for overlays
    ALPHA_PANEL = 25                  # Panel transparency (0-255)
    ALPHA_OVERLAY = 51                # Overlay transparency (0-255)
    ALPHA_GLOW = 127                  # Glow effect transparency (0-255)

    @classmethod
    def get_gradient_colors(cls, start_color, end_color):
        """
        Helper method to get gradient color pairs for pygame_gui
        Returns tuple of (start_color, end_color) for gradient effects
        """
        return (start_color, end_color)
    
    @classmethod
    def get_button_gradient(cls):
        """Returns the primary button gradient colors"""
        return cls.get_gradient_colors(cls.BUTTON_BG_PRIMARY, cls.BUTTON_BG_SECONDARY)
    
    @classmethod
    def get_progress_gradient(cls):
        """Returns the progress bar gradient colors"""
        return cls.get_gradient_colors(cls.PROGRESS_FILL_START, cls.PROGRESS_FILL_END)
    
    @classmethod
    def get_panel_gradient(cls):
        """Returns the panel background gradient colors"""
        return cls.get_gradient_colors(cls.BG_PANEL_PRIMARY, cls.BG_PANEL_SECONDARY)

# Color schemes for different UI states
class VaporwaveStates:
    """
    State-based color configurations for dynamic UI elements
    """
    
    STATUS_COLORS = {
        'running': VaporwaveColors.TEXT_GREEN,
        'stopped': VaporwaveColors.TEXT_RED,
        'paused': VaporwaveColors.TEXT_YELLOW,
        'error': VaporwaveColors.TEXT_RED,
        'connecting': VaporwaveColors.TEXT_CYAN
    }
    
    BUTTON_STATES = {
        'normal': VaporwaveColors.BUTTON_BG_PRIMARY,
        'hovered': VaporwaveColors.BUTTON_BG_HOVER,
        'pressed': VaporwaveColors.BUTTON_BG_SECONDARY,
        'disabled': "#333333",
        'active': VaporwaveColors.BUTTON_BG_ACTIVE
    }
    
    PANEL_TYPES = {
        'primary': VaporwaveColors.BG_PANEL_PRIMARY,
        'secondary': VaporwaveColors.BG_PANEL_SECONDARY,
        'game_area': VaporwaveColors.BG_GAME_AREA,
        'overlay': VaporwaveColors.BG_OVERLAY_PANEL
    }

# Font configurations for the theme
class VaporwaveFonts:
    """
    Font configurations for the vaporwave theme
    """
    
    # Font names (ensure these are installed or use fallbacks)
    PRIMARY_FONT = "Orbitron"         # Primary UI font
    MONOSPACE_FONT = "Share Tech Mono" # Monospace for terminal-style text
    FALLBACK_FONT = "Courier New"     # Fallback monospace
    
    # Font sizes
    TITLE_SIZE = 14                   # Panel titles
    BUTTON_SIZE = 10                  # Button text
    LABEL_SIZE = 10                   # Labels
    TEXT_SIZE = 9                     # Text boxes
    METRIC_SIZE = 11                  # Metric displays
    
    # Font weights (if supported by pygame_gui)
    WEIGHT_NORMAL = "normal"
    WEIGHT_BOLD = "bold"
    WEIGHT_HEAVY = "900"

# Layout constants
class VaporwaveLayout:
    """
    Layout constants for the vaporwave interface
    """
    
    # Main window dimensions
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    # Panel dimensions
    CONTROL_PANEL_WIDTH = 400
    BROWSER_PANEL_WIDTH = 800
    
    # Margins and padding
    PANEL_MARGIN = 10
    PANEL_PADDING = 12
    BUTTON_MARGIN = 2
    COMPONENT_SPACING = 6
    
    # Border widths
    MAIN_BORDER_WIDTH = 3
    PANEL_BORDER_WIDTH = 2
    BUTTON_BORDER_WIDTH = 2
    
    # Component heights
    BUTTON_HEIGHT = 30
    SLIDER_HEIGHT = 20
    PROGRESS_HEIGHT = 20
    DROPDOWN_HEIGHT = 25
    TEXTBOX_MIN_HEIGHT = 60
    
    # Game area dimensions
    GAME_AREA_WIDTH = 760
    GAME_AREA_HEIGHT = 560
    OVERLAY_PANEL_HEIGHT = 140