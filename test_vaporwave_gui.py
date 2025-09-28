#!/usr/bin/env python3
"""
Simple test of the vaporwave GUI without bot dependencies
"""

import sys
from pathlib import Path

# Add GUI directory to path
sys.path.append(str(Path(__file__).parent / "gui"))

from vaporwave_interface import VaporwaveInterface

def main():
    """Test the vaporwave interface standalone"""
    print("🌸 Testing JED-2048 Vaporwave Interface")
    print("=" * 50)
    print("✨ Features to test:")
    print("   - Vaporwave 1984 aesthetic")
    print("   - Interactive buttons with hover effects")
    print("   - Real-time status updates")
    print("   - Professional panel layout")
    print("\n🎮 Interface launching...")

    # Create and run interface
    interface = VaporwaveInterface()

    # Add some test data
    interface.update_metrics({
        'score': 4096,
        'moves': 200,
        'efficiency': 20.48,
        'algorithm': 'Enhanced Heuristic',
        'fps': 30
    })

    # Run the interface
    interface.run()

if __name__ == "__main__":
    main()