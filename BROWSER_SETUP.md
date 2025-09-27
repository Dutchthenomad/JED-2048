# [LEGACY] Browser Standardization for 2048 Bot Testing

Note: This document contains legacy Selenium/Firefox guidance kept for historical context. For the current Playwright-based setup, use `PLAYWRIGHT_SETUP_INSTRUCTIONS.md` and the Playwright tools under `tools/`.

## Required Browser Setup

### Browser: Chromium via Playwright (Current Standard)
See `PLAYWRIGHT_SETUP_INSTRUCTIONS.md` for installation and verification steps.

### Game Target: 2048game.com or play2048.co
**Why:** Original implementation, clean design, consistent colors, no ads/distractions

## Essential Browser Configuration

### 1. Browser Settings
```bash
# Open Firefox
firefox

# Navigate to target
# URL: https://gabrielecirulli.github.io/2048/
```

### 2. Display Settings
- **Zoom Level**: 100% (Ctrl+0 to reset)
- **Window Mode**: Full-screen (F11) or consistent windowed size
- **No browser UI interference**: Use full-screen mode for testing

### 3. Disable Animations (Optional but Recommended)
```
1. Type 'about:config' in address bar
2. Accept risk warning
3. Search for 'layout.animated'
4. Set to 'false' for more predictable screenshots
```

## Pre-Test Verification Checklist

### Before running any bot tests:
- [ ] Firefox is open with 2048 game loaded
- [ ] Game is in full-screen mode (F11)
- [ ] Zoom is at 100%
- [ ] Game board is fully visible
- [ ] No browser notifications/popups visible
- [ ] Game is in a playable state (not game over)

## Standardized Game State for Initial Testing

### For consistent testing, start with:
1. **Fresh game**: Click "New Game" button
2. **Known initial state**: Two tiles visible (usually two 2's)
3. **Board visible**: 4x4 grid clearly displayed
4. **No overlays**: No menus, popups, or dialogs open

## Screen Resolution Considerations

### Recommended minimum resolution: 1024x768
- Game board should be clearly visible
- No horizontal/vertical scrolling required
- Board tiles are large enough for accurate capture

## Multiple Monitor Setup

### If using multiple monitors:
- **Primary monitor**: Place game on primary monitor (monitor 0)
- **Consistent positioning**: Always use same monitor for testing
- **No spanning**: Game window should not span multiple monitors

## Troubleshooting Common Issues

### Game not visible in screenshots:
1. Ensure Firefox is the active window
2. Check if game is in viewport (no scrolling needed)
3. Verify full-screen mode is enabled
4. Check for browser zoom settings

### Color recognition issues:
1. Verify monitor color profile is standard
2. Check browser dark mode is disabled
3. Ensure game theme is default (not dark/custom theme)

## Testing Commands

### Option 1: Easy Capture (Recommended)
```bash
cd "/home/nomad/Desktop/SOLANA EDU/2048-playwright-fork/2048-demo"
source ../venv/bin/activate

# Single capture with 8-second delay (comfortable timing)
python tools/easy_capture.py

# Custom timing: 10-second delay
python tools/easy_capture.py 10

# Multiple captures: 8s delay, 3 captures
python tools/easy_capture.py 8 3
```

### Option 2: Interactive Browser Verification (Playwright)
```bash
python tools/verify_browser_setup.py  # Playwright-based checks
```

### Window Management Tips

**For clear captures without terminal overlay:**

1. **Dual Monitor Setup (Recommended):**
   - Run terminal on one monitor
   - Open 2048 game on the other monitor
   - No switching needed during capture

2. **Single Monitor Setup:**
   - Use delayed capture tool (gives you time to switch)
   - Or minimize terminal after running command
   - Or use Alt+Tab to switch to browser during countdown

3. **Browser Window Positioning:**
   - Full-screen (F11) is ideal for consistent captures
   - Or use consistent windowed size (1200x800 minimum)
   - Ensure game board is not cut off by screen edges

This ensures screenshots capture the game clearly without terminal interference.
