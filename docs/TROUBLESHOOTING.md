# 2048 Bot Troubleshooting Guide

## Quick Diagnostic Commands

Run these commands to diagnose common issues:

```bash
# Test core functionality
python3 -c "from complete_2048_bot import Complete2048Bot; print('✅ Import successful')"

# Test browser availability
python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); print('Chromium:', bool(p.chromium.executable_path)); print('Firefox:', bool(p.firefox.executable_path)); print('WebKit:', bool(p.webkit.executable_path)); p.stop()"

# Test cross-browser compatibility
python3 test_cross_browser_compatibility.py

# Test strategy system
python3 test_enhanced_strategy.py
```

## Error Categories

### 1. Import and Module Errors

#### Error: `ModuleNotFoundError: No module named 'playwright'`
**Cause**: Playwright not installed
**Solution**:
```bash
source venv/bin/activate
pip install playwright
playwright install
```

#### Error: `ImportError: cannot import name 'Complete2048Bot'`
**Cause**: Module path issues or syntax errors
**Solution**:
```bash
# Check for syntax errors
python3 -m py_compile complete_2048_bot.py

# Verify file exists
ls -la complete_2048_bot.py

# Check Python path
python3 -c "import sys; print(sys.path)"
```

### 2. Browser Connection Issues

#### Error: `❌ Connection failed` or `Browser launch failed`
**Symptoms**: Bot cannot connect to any 2048 site
**Diagnosis**:
```bash
# Test network connectivity
curl -I https://2048game.com/
ping 2048game.com

# Test browser installation
playwright install --with-deps chromium
```

**Solutions**:
1. **Network Issues**:
   ```python
   # Try different URLs
   bot.connect_to_game("https://gabrielecirulli.github.io/2048/")
   bot.connect_to_game("https://play2048.co/")
   ```

2. **Firewall/Proxy Issues**:
   ```python
   # Disable ad blocking
   controller = PlaywrightController(block_ads=False)
   ```

3. **Browser Installation Issues**:
   ```bash
   # Reinstall browsers
   playwright uninstall
   playwright install --with-deps
   ```

#### Error: `TimeoutError: Timeout 30000ms exceeded`
**Cause**: Slow network or overloaded system
**Solution**:
```python
# Increase timeout
controller = PlaywrightController()
# Modify connect method timeout in playwright_controller.py
# Change: self.page.goto(url, timeout=60000) to timeout=120000
```

### 3. Vision System Issues

#### Error: `❌ Board analysis failed` or `Vision system failed`
**Symptoms**: Cannot detect tiles or board state
**Diagnosis**:
```python
# Enable debug mode to save screenshots
bot = Complete2048Bot(debug=True)
# Check generated PNG files for visual issues
```

**Solutions**:
1. **Display Scaling Issues**:
   - Set system display scaling to 100%
   - Use headless mode: `headless=True`

2. **Browser Rendering Issues**:
   ```python
   # Try different browser
   controller = PlaywrightController(browser_type="firefox")
   # or
   controller = PlaywrightController(browser_type="webkit")
   ```

3. **Color Detection Issues**:
   ```python
   # Verify canonical colors are detected
   from core.canonical_vision import CanonicalBoardVision
   vision = CanonicalBoardVision()
   # Check screenshot manually for color accuracy
   ```

#### Error: `Board detected: [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]`
**Cause**: Game not initialized or vision not detecting tiles
**Solutions**:
1. **Wait for game initialization**:
   ```python
   # Increase initialization wait time
   time.sleep(5)  # Wait longer before first analysis
   ```

2. **Force game start**:
   ```python
   # Add manual game start
   controller.send_key('ArrowUp')  # Trigger first move
   time.sleep(2)
   ```

### 4. Strategy and Move Issues

#### Error: `❌ input simulation insufficient (0/3 moves)`
**Cause**: Moves not affecting game state (normal for empty board)
**Verification**:
```python
# Check if moves work on populated board
# This is often normal behavior - empty board doesn't change
# Test with actual game in progress
```

#### Error: Poor strategy performance (low scores)
**Diagnosis**:
```python
# Test strategy components
python3 test_enhanced_strategy.py

# Check strategy weights
bot = Complete2048Bot()
print(bot.strategy.weights)
```

**Solutions**:
1. **Use optimized weights**:
   ```python
   bot.strategy.weights = {
       'empty_tiles': 150.0,
       'merge_potential': 100.0,
       'corner_bonus': 250.0,
       'monotonicity': 75.0,
       'max_tile_value': 15.0
   }
   ```

2. **Test weight configurations**:
   ```bash
   python3 weight_tuning_framework.py
   ```

### 5. Performance Issues

#### Error: High memory usage or slow execution
**Symptoms**: Bot runs slowly or uses excessive resources
**Solutions**:
1. **Enable headless mode**:
   ```python
   bot = Complete2048Bot(headless=True, debug=False)
   ```

2. **Reduce screenshot saving**:
   ```python
   # Disable debug mode in production
   bot = Complete2048Bot(debug=False)
   ```

3. **Optimize browser**:
   ```python
   # Use fastest browser
   controller = PlaywrightController(browser_type="chromium")
   ```

4. **Clean up regularly**:
   ```python
   # Manual cleanup
   bot.cleanup()

   # Or use context manager
   with Complete2048Bot() as bot:
       # Automatic cleanup
       pass
   ```

### 6. Error Handler Issues

#### Error: `Maximum error count (5) reached`
**Cause**: Too many consecutive errors
**Solutions**:
1. **Reset error count**:
   ```python
   bot.error_handler.reset_error_count()
   ```

2. **Investigate root cause**:
   ```bash
   # Check logs
   tail -f logs/2048_bot_*.log
   grep "ERROR" logs/2048_bot_*.log
   ```

3. **Adjust error thresholds**:
   ```python
   bot.error_handler.max_errors = 10  # Increase tolerance
   ```

## Environment-Specific Issues

### Linux Issues

#### Error: `Error: browserType.launch: Executable doesn't exist`
**Cause**: Missing browser dependencies
**Solution**:
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
    libgtk-3-0 libxss1 libasound2

# Reinstall with dependencies
playwright install --with-deps
```

#### Error: `No DISPLAY variable set`
**Cause**: Running GUI mode without display
**Solutions**:
1. **Use headless mode**:
   ```python
   bot = Complete2048Bot(headless=True)
   ```

2. **Set up virtual display**:
   ```bash
   sudo apt-get install xvfb
   xvfb-run -a python3 complete_2048_bot.py
   ```

### macOS Issues

#### Error: `zsh: command not found: playwright`
**Cause**: PATH issues or virtual environment not activated
**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate
which python3  # Should show venv path

# Reinstall if needed
pip install playwright
playwright install
```

### Windows Issues

#### Error: `'playwright' is not recognized as an internal or external command`
**Cause**: Windows PATH or virtual environment issues
**Solution**:
```cmd
# Activate virtual environment
venv\Scripts\activate

# Verify installation
pip list | findstr playwright
playwright --version
```

## Debugging Techniques

### 1. Enable Comprehensive Logging
```python
bot = Complete2048Bot(debug=True, log_level="DEBUG")
```

### 2. Manual Step-by-Step Testing
```python
# Test each component individually
from core.playwright_controller import PlaywrightController
from core.canonical_vision import CanonicalBoardVision
from core.strategy import BasicStrategy

# Test browser
controller = PlaywrightController(headless=False)
success = controller.connect()
print(f"Connection: {success}")

# Test vision
screenshot = controller.take_screenshot("debug_test.png")
vision = CanonicalBoardVision()
result = vision.analyze_board(screenshot)
print(f"Vision: {result}")

# Test strategy
strategy = BasicStrategy()
scores = strategy.get_move_scores([[2,4,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]])
print(f"Strategy: {scores}")
```

### 3. Screenshot Analysis
```python
# Enable debug screenshots
bot = Complete2048Bot(debug=True)
# Screenshots saved as: bot_move_XXX_before.png, bot_move_XXX_after.png
# Examine these files to understand vision issues
```

### 4. Performance Monitoring
```python
import time
import psutil
import os

def monitor_performance():
    process = psutil.Process(os.getpid())
    print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
    print(f"CPU: {process.cpu_percent():.1f}%")

# Call during bot operation
monitor_performance()
```

## Recovery Procedures

### 1. Full Reset
```bash
# Complete environment reset
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps
```

### 2. Clear Temporary Files
```bash
# Remove debug artifacts
rm -f *.png
rm -f logs/*.log
rm -rf __pycache__/
rm -rf core/__pycache__/
```

### 3. Network Connectivity Test
```bash
# Test all game URLs
for url in "https://2048game.com/" "https://gabrielecirulli.github.io/2048/" "https://play2048.co/"; do
    echo "Testing $url"
    curl -I "$url" 2>/dev/null | head -1
done
```

## Getting Additional Help

### 1. Collect Diagnostic Information
```bash
# System information
python3 --version
pip list | grep -E "(playwright|opencv|numpy)"
playwright --version

# Test basic functionality
python3 -c "
import sys, platform, cv2, numpy, playwright
print(f'Python: {sys.version}')
print(f'Platform: {platform.system()} {platform.release()}')
print(f'OpenCV: {cv2.__version__}')
print(f'NumPy: {numpy.__version__}')
print(f'Playwright: {playwright.__version__}')
"
```

### 2. Create Minimal Test Case
```python
# Minimal reproduction script
from complete_2048_bot import Complete2048Bot

try:
    bot = Complete2048Bot(headless=True, debug=True)
    success = bot.connect_to_game()
    print(f"Connection successful: {success}")
    bot.cleanup()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

### 3. Log Analysis Commands
```bash
# Find recent errors
find logs/ -name "*.log" -mtime -1 -exec grep -l "ERROR" {} \;

# Count error types
grep "ERROR" logs/*.log | cut -d: -f3 | sort | uniq -c

# Timeline of issues
grep -h "ERROR\|WARNING" logs/*.log | sort
```

---

**Remember**: Most issues are environment-related. Start with the diagnostic commands and work through the solutions systematically. The error handler provides detailed logging to help identify root causes.