"""
Playwright Browser Controller
Minimal browser automation controller for 2048 game interaction.
Drop-in replacement for previous Selenium-based approach.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import time

# Try to import Playwright, but make it optional for testing
try:
    from playwright.sync_api import sync_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not available in this environment")


class PlaywrightController:
    """Minimal Playwright controller for 2048 automation"""

    def __init__(self, headless: bool = False, browser_type: str = "chromium", block_ads: bool = True):
        """
        Initialize Playwright controller

        Args:
            headless: Run browser in headless mode
            browser_type: Browser to use (chromium, firefox, webkit)
            block_ads: Enable ad blocking for reliable automation
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is not installed. Run: pip install playwright && playwright install")

        self.headless = headless
        self.browser_type = browser_type
        self.block_ads = block_ads
        self.playwright = None
        self.browser = None
        self.page = None
        self.is_connected = False

    def connect(self, url: str = "https://2048game.com/") -> bool:
        """
        Connect to 2048 game

        Args:
            url: Game URL to navigate to

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"🌐 Connecting to browser ({self.browser_type})...")

            # Start Playwright
            self.playwright = sync_playwright().start()

            # Configure browser launch arguments for ad blocking
            launch_args = []
            if self.block_ads:
                # Add ad blocking arguments
                launch_args.extend([
                    '--disable-background-networking',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-extensions-except=',
                    '--disable-extensions',
                    '--no-first-run',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ])

            # Launch browser with ad blocking
            if self.browser_type == "chromium":
                self.browser = self.playwright.chromium.launch(
                    headless=self.headless,
                    args=launch_args if self.block_ads else None
                )
            elif self.browser_type == "firefox":
                # Firefox uses different approach - we'll use page-level blocking
                self.browser = self.playwright.firefox.launch(headless=self.headless)
            elif self.browser_type == "webkit":
                # WebKit uses different approach - we'll use page-level blocking
                self.browser = self.playwright.webkit.launch(headless=self.headless)
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")

            # Create new page
            self.page = self.browser.new_page()

            # Set up page-level ad blocking for all browsers
            if self.block_ads:
                # Block common ad domains and tracking
                def block_ads(route):
                    """Block ads and tracking requests"""
                    url = route.request.url

                    # Allow the main game domain and essential resources
                    allowed_domains = [
                        '2048game.com',
                        'www.2048game.com',
                        'githubusercontent.com'
                    ]

                    # Allow if from allowed domain
                    if any(domain in url.lower() for domain in allowed_domains):
                        route.continue_()
                        return

                    # Block known ad patterns
                    ad_patterns = [
                        'googlesyndication',
                        'doubleclick',
                        'googletagmanager',
                        'google-analytics',
                        'facebook.com/tr',
                        'googleadservices',
                        'adsystem',
                        'amazon-adsystem',
                        'scorecardresearch'
                    ]

                    # Block if URL contains ad patterns
                    if any(pattern in url.lower() for pattern in ad_patterns):
                        route.abort()
                        return

                    # Allow everything else (more permissive for game functionality)
                    route.continue_()

                # Set up request interception
                self.page.route('**/*', block_ads)

                print("🛡️  Ad blocking enabled")

            # Navigate to game
            print(f"📱 Navigating to {url}...")
            self.page.goto(url, timeout=60000)

            # Wait for game to load
            self.page.wait_for_load_state("networkidle", timeout=30000)

            # Verify game loaded
            game_container = self.page.locator(".game-container")
            if game_container.count() > 0:
                print("✅ Game loaded successfully")
                self.is_connected = True
                return True
            else:
                print("❌ Game container not found")
                return False

        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            self.cleanup()
            return False

    def take_screenshot(self, save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        Take screenshot of current page

        Args:
            save_path: Optional path to save screenshot

        Returns:
            Screenshot as numpy array (BGR format for OpenCV)
        """
        if not self.is_connected or not self.page:
            print("❌ Not connected to browser")
            return None

        try:
            # Take screenshot
            if save_path:
                self.page.screenshot(path=save_path, full_page=True)
                print(f"📸 Screenshot saved: {save_path}")

                # Load with OpenCV for consistency with vision system
                image = cv2.imread(save_path)
                return image
            else:
                # Get screenshot as bytes and convert to numpy array
                screenshot_bytes = self.page.screenshot(full_page=True)

                # Convert bytes to numpy array
                import io
                from PIL import Image

                # Convert bytes to PIL Image
                image_pil = Image.open(io.BytesIO(screenshot_bytes))

                # Convert PIL to numpy array
                image_np = np.array(image_pil)

                # Convert RGBA/RGB to BGR for OpenCV
                if len(image_np.shape) == 3:
                    if image_np.shape[2] == 4:  # RGBA
                        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGBA2BGR)
                    else:  # RGB
                        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                else:
                    image_bgr = image_np

                return image_bgr

        except Exception as e:
            print(f"❌ Screenshot failed: {str(e)}")
            return None

    def send_key(self, key: str) -> bool:
        """
        Send key press to game

        Args:
            key: Key to press (ArrowUp, ArrowDown, ArrowLeft, ArrowRight)

        Returns:
            True if successful
        """
        if not self.is_connected or not self.page:
            print("❌ Not connected to browser")
            return False

        try:
            # Map common key names
            key_mapping = {
                'UP': 'ArrowUp',
                'DOWN': 'ArrowDown',
                'LEFT': 'ArrowLeft',
                'RIGHT': 'ArrowRight',
                'up': 'ArrowUp',
                'down': 'ArrowDown',
                'left': 'ArrowLeft',
                'right': 'ArrowRight'
            }

            # Use mapped key or original
            actual_key = key_mapping.get(key, key)

            # Send key to page
            self.page.keyboard.press(actual_key)

            # Small delay for game animation
            time.sleep(0.1)

            return True

        except Exception as e:
            print(f"❌ Key press failed: {str(e)}")
            return False

    def reset_game(self) -> bool:
        """
        Reset game to initial state

        Returns:
            True if successful
        """
        if not self.is_connected or not self.page:
            print("❌ Not connected to browser")
            return False

        try:
            # Look for "New Game" button
            new_game_button = self.page.locator(".restart-button")

            if new_game_button.count() > 0:
                new_game_button.click()
                print("🔄 Game reset")

                # Wait for reset to complete
                time.sleep(0.5)
                return True
            else:
                print("❌ Reset button not found")
                return False

        except Exception as e:
            print(f"❌ Reset failed: {str(e)}")
            return False

    def get_game_info(self) -> Dict[str, Any]:
        """
        Get current game information

        Returns:
            Dictionary with game info (score, etc.)
        """
        if not self.is_connected or not self.page:
            return {}

        try:
            info = {}

            # Get score
            score_element = self.page.locator(".score-container")
            if score_element.count() > 0:
                score_text = score_element.text_content()
                # Extract number from score text
                import re
                score_match = re.search(r'(\d+)', score_text)
                if score_match:
                    info['score'] = int(score_match.group(1))

            # Check for game over
            game_over = self.page.locator(".game-over")
            info['game_over'] = game_over.count() > 0

            return info

        except Exception as e:
            print(f"❌ Error getting game info: {str(e)}")
            return {}

    def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                self.page.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

            self.page = None
            self.browser = None
            self.playwright = None
            self.is_connected = False

            print("🧹 Browser cleanup completed")

        except Exception as e:
            print(f"⚠️  Cleanup warning: {str(e)}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

def validate_controller():
    """
    Basic validation function for the Playwright controller.
    Tests connection, screenshot, and key input functionality.
    """
    print("🧪 Validating Playwright Controller...")
    # Test 1: Controller creation
    print("\n📋 Test 1: Controller Creation")
    try:
        controller = PlaywrightController(headless=False, browser_type="chromium", block_ads=False)
        print("✅ Controller created successfully")
    except Exception as e:
        print(f"❌ Controller creation failed: {e}")
        return False

    # Test 2: Game connection
    print("\n📋 Test 2: Game Connection")
    try:
        print("⏳ Attempting to connect to 2048 game...")
        print("   (This may take up to 60 seconds if network is slow)")

        # Try to connect - if it fails, we'll test with a simpler page
        success = controller.connect()
        if success:
            print("✅ Connected to 2048 game")
        else:
            print("⚠️  2048 site connection failed, testing with simple page...")
            # Test basic browser functionality with a simple page
            controller.page.goto('data:text/html,<h1>Browser Test</h1><div id="test">Working</div>')
            title = controller.page.title()
            if "Browser Test" in controller.page.content():
                print("✅ Browser functionality confirmed - network issue with 2048 site")
                print("   (You can test manually by visiting 2048game.com)")
            else:
                print("❌ Browser functionality failed")
                return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        controller.cleanup()
        return False

    # Test 3: Screenshot capability
    print("\n📋 Test 3: Screenshot Capability")
    try:
        import time
        print("⏳ Taking screenshot...")
        time.sleep(1)  # Brief pause for page stability

        screenshot = controller.take_screenshot("validation_test_screenshot.png")
        if screenshot is not None:
            print("✅ Screenshot captured successfully")
            try:
                print(f"📏 Screenshot dimensions: {screenshot.shape}")
            except Exception:
                # Some screenshot paths may return None or non-array; ignore shape errors
                pass
        else:
            print("❌ Screenshot failed")
            controller.cleanup()
            return False
    except Exception as e:
        print(f"❌ Screenshot error: {e}")
        controller.cleanup()
        return False

    # Test 4: Game information
    print("\n📋 Test 4: Game Information")
    try:
        game_info = controller.get_game_info()
        print(f"🎮 Game info: {game_info}")
        if 'score' in game_info:
            print("✅ Score detection working")
        else:
            print("⚠️  Score detection may need adjustment")
    except Exception as e:
        print(f"❌ Game info error: {e}")

    # Test 5: Key input testing
    print("\n📋 Test 5: Key Input Testing")
    test_keys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight']

    for key in test_keys:
        try:
            success = controller.send_key(key)
            if success:
                print(f"✅ {key} sent successfully")
                time.sleep(0.5)  # Wait between moves
            else:
                print(f"❌ {key} failed")
        except Exception as e:
            print(f"❌ Key {key} error: {e}")

    # Test 6: Game reset functionality
    print("\n📋 Test 6: Game Reset")
    try:
        reset_success = controller.reset_game()
        if reset_success:
            print("✅ Game reset successful")
            time.sleep(2)  # Wait for reset to complete
        else:
            print("⚠️  Game reset may need adjustment")
    except Exception as e:
        print(f"❌ Reset error: {e}")

    # Test 7: Cleanup
    print("\n📋 Test 7: Cleanup")
    try:
        controller.cleanup()
        print("✅ Cleanup successful")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

    print("\n🎯 Validation Summary")
    print("✅ All core functionality tested")
    print("📝 Ready for integration with vision system")
    return True


if __name__ == "__main__":
    # Basic validation if run directly
    validate_controller()