#!/usr/bin/env python3
"""
Easy Capture Tool for 2048 Bot Development
Optimized timing for comfortable window management.

Usage:
    python tools/easy_capture.py [delay_seconds] [count]
"""

import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def easy_capture(delay_seconds=8, count=1, interval=3):
    """
    Easy capture with comfortable timing for window management

    Args:
        delay_seconds: Time to minimize terminal and maximize browser
        count: Number of screenshots to take
        interval: Time between multiple screenshots
    """

    print("📸 Easy 2048 Game Capture")
    print("=" * 30)
    print(f"⏱️  Delay: {delay_seconds} seconds (plenty of time!)")
    print(f"📷 Captures: {count}")

    if count > 1:
        print(f"⏳ Interval: {interval} seconds between shots")

    # Setup output directory
    output_dir = project_root / "validation_data" / "easy_captures"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🎯 Instructions:")
    print(f"   1. Open Firefox with 2048 game ready")
    print(f"   2. Press Enter to start {delay_seconds}-second countdown")
    print(f"   3. Minimize this terminal (click minimize button)")
    print(f"   4. Maximize Firefox to full screen (F11 or maximize)")
    print(f"   5. Screenshots will happen automatically")
    print(f"   6. Come back to terminal when done")

    input("\nPress Enter when 2048 game is ready...")

    print(f"\n⏰ Starting {delay_seconds}-second countdown...")
    print(f"   💡 TIP: Minimize terminal and maximize browser NOW!")

    # Extended countdown with helpful reminders
    for i in range(delay_seconds, 0, -1):
        if i == delay_seconds:
            print(f"   {i}... (minimize terminal now)")
        elif i == delay_seconds - 2:
            print(f"   {i}... (maximize Firefox)")
        elif i == delay_seconds - 4:
            print(f"   {i}... (ensure 2048 game visible)")
        elif i <= 3:
            print(f"   {i}... (almost ready)")
        else:
            print(f"   {i}...")
        time.sleep(1)

    print("\n📸 CAPTURING SCREENSHOTS!")

    successful_captures = 0
    failed_captures = 0

    for capture_num in range(count):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"2048_capture_{timestamp}_{capture_num+1:02d}.png"
            output_path = output_dir / filename

            print(f"\n   📷 Taking capture {capture_num + 1}/{count}...")

            # Use gnome-screenshot (works with Wayland)
            result = subprocess.run([
                'gnome-screenshot',
                '-f', str(output_path)
            ], capture_output=True, text=True)

            if result.returncode == 0 and output_path.exists():
                file_size = output_path.stat().st_size
                print(f"   ✅ Success: {filename}")
                print(f"   📏 Size: {file_size:,} bytes")

                if file_size > 50000:  # Good size for full screenshot
                    successful_captures += 1
                    print(f"   🎉 Capture quality looks good!")
                else:
                    print(f"   ⚠️  Small file size, check quality")

            else:
                print(f"   ❌ Capture failed: {result.stderr}")
                failed_captures += 1

            # Wait between captures
            if capture_num < count - 1:
                print(f"   ⏳ Waiting {interval}s for next capture...")
                for wait_sec in range(interval, 0, -1):
                    print(f"      {wait_sec}...")
                    time.sleep(1)

        except Exception as e:
            print(f"   ❌ Error during capture {capture_num + 1}: {e}")
            failed_captures += 1

    # Summary
    print(f"\n📊 Capture Session Complete!")
    print(f"   ✅ Successful: {successful_captures}")
    print(f"   ❌ Failed: {failed_captures}")
    print(f"   📁 Location: {output_dir}")

    if successful_captures > 0:
        print(f"\n🔍 Next Steps:")
        print(f"   1. Check captured images in: {output_dir}")
        print(f"   2. Verify 2048 game board is clearly visible")
        print(f"   3. Look for clean, full-screen captures")
        print(f"   4. These will be used for vision system development")

        return True
    else:
        print(f"\n🔧 Troubleshooting:")
        print(f"   1. Ensure gnome-screenshot is installed")
        print(f"   2. Try with Firefox in full-screen mode (F11)")
        print(f"   3. Make sure game is loaded and visible")

        return False

def main():
    """Main function with flexible timing options"""

    print("🚀 2048 Bot Development - Easy Capture Tool")
    print("=" * 50)

    # Parse command line arguments
    delay = 8  # Default: 8 seconds (comfortable)
    count = 1  # Default: single capture

    if len(sys.argv) > 1:
        try:
            delay = int(sys.argv[1])
        except ValueError:
            print("Invalid delay, using 8 seconds")

    if len(sys.argv) > 2:
        try:
            count = int(sys.argv[2])
        except ValueError:
            print("Invalid count, using 1 capture")

    # Validate timing
    if delay < 3:
        print("⚠️  Warning: Delay less than 3 seconds may not give enough time")
        proceed = input("Continue anyway? (y/n): ").lower().strip()
        if proceed != 'y':
            print("👋 Cancelled. Use longer delay for easier window management.")
            return

    if count > 10:
        print("⚠️  Warning: More than 10 captures will take a while")
        proceed = input("Continue anyway? (y/n): ").lower().strip()
        if proceed != 'y':
            print("👋 Cancelled. Use smaller count for quicker testing.")
            return

    # Run capture
    success = easy_capture(delay, count)

    if success:
        print(f"\n🎉 Capture successful! Ready for vision system development.")
    else:
        print(f"\n🔧 Capture had issues. Check troubleshooting steps above.")

if __name__ == "__main__":
    main()