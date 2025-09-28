"""
JED-2048 Debug GUI Package
Real-time visualization interface for bot operation and development
"""

# Only import working components (avoid pygame_gui conflicts)
from .gui_config import GUIConfig
from .vaporwave_colors import VaporwaveColors
from .debug_interface import DebugInterface

__all__ = [
    'GUIConfig',
    'VaporwaveColors',
    'DebugInterface'
]

__version__ = "1.0.0"
