# Playwright Setup Instructions for 2048-Demo

## Quick Setup Commands

### Step 1: Install Playwright in the 2048-demo environment
```bash
cd "/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo"
source venv/bin/activate
pip install playwright>=1.55.0
```

### Step 2: Install Playwright browsers
```bash
# Still in the activated environment
playwright install
```

### Step 3: Install system dependencies (in separate terminal)
```bash
# Open a NEW terminal (don't use the venv terminal)
sudo playwright install-deps
# OR if that doesn't work:
sudo apt-get install libevent-2.1-7t64
```

### Step 4: Verify installation
```bash
# Back in the venv terminal
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright ready!')"
```

## Complete Setup Verification

Run this complete setup sequence:

```bash
# Terminal 1 (for main setup)
cd "/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo"
source venv/bin/activate
pip install playwright>=1.55.0
playwright install

# Test import
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright imported successfully')"
```

```bash
# Terminal 2 (for sudo commands - run this in parallel)
sudo playwright install-deps
```

## Implementation Workflow

After setup, you can implement the validation function:

1. **Open the file**: `/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo/core/playwright_controller.py`

2. **Find the TODO**: Look for `TODO(human): Add basic validation function`

3. **Follow the guide**: Use `/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo/VALIDATION_GUIDE.md`

4. **Test your implementation**:
   ```bash
   cd "/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo"
   source venv/bin/activate
   python core/playwright_controller.py
   ```

## Key Points for Implementation

### Timing Considerations (Based on Your Game Loading Insight)
```python
# After connecting, always wait for initial tiles to appear
controller.connect()
time.sleep(3)  # Critical timing for game initialization
screenshot = controller.take_screenshot()
```

### Error Handling Template
```python
try:
    # Your test code here
    print("✅ Test passed")
    return True
except Exception as e:
    print(f"❌ Test failed: {e}")
    controller.cleanup()
    return False
```

### Context Manager Usage (Recommended)
```python
def validate_controller():
    with PlaywrightController(headless=False) as controller:
        if not controller.connect():
            return False

        # All your validation tests here

        return True  # Cleanup happens automatically
```

## Troubleshooting

### If you get "Browser not found" errors:
```bash
playwright install
```

### If you get permission errors:
```bash
# Run in separate terminal (not the venv one)
sudo playwright install-deps
```

### If imports fail:
```bash
# Make sure you're in the right environment
source venv/bin/activate
pip install playwright
```

## What to Implement

Your `validate_controller()` function should test these core features:

1. ✅ **Controller Creation**: `PlaywrightController(headless=False)`
2. ✅ **Game Connection**: `controller.connect()`
3. ✅ **Screenshot Capture**: `controller.take_screenshot()`
4. ✅ **Key Input**: `controller.send_key('ArrowUp')`
5. ✅ **Game Reset**: `controller.reset_game()`
6. ✅ **Game Info**: `controller.get_game_info()`
7. ✅ **Cleanup**: `controller.cleanup()`

## Success Criteria

When your implementation works correctly:
- Browser opens and loads 2048 game
- Screenshots are captured successfully
- Arrow keys move tiles in the game
- Game reset button works
- No error messages during cleanup

## Ready for Next Phase

Once validation passes, we'll integrate:
- Vision system analysis of Playwright screenshots
- Strategy system recommendations
- Complete automation pipeline testing

This completes the migration from Selenium to Playwright!