# 2048 Bot Integration Guide

## Overview

This guide provides comprehensive instructions for integrating, deploying, and troubleshooting the production-ready 2048 bot. The bot combines Playwright browser automation, computer vision, and AI strategy for autonomous gameplay.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage Examples](#usage-examples)
6. [Architecture Overview](#architecture-overview)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tuning](#performance-tuning)
10. [API Reference](#api-reference)

## System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10/11
- **Python**: 3.8+
- **Memory**: 2GB RAM available
- **Storage**: 500MB free space
- **Network**: Stable internet connection

### Recommended Requirements
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.10+
- **Memory**: 4GB RAM available
- **Storage**: 1GB free space
- **Display**: For visible mode testing

### Dependencies
- Playwright (with browser engines)
- OpenCV (computer vision)
- NumPy (numerical processing)
- Python standard library modules

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd 2048-playwright-fork/2048-demo
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows
pip install -r requirements.txt
playwright install
```

### 2. Run Basic Test
```bash
python3 run_visible_bot.py
```

### 3. Cross-Browser Test
```bash
python3 test_cross_browser_compatibility.py
```

## Installation

### Virtual Environment Setup
```bash
# Create isolated environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium firefox webkit
```

### Verify Installation
```bash
# Test core components
python3 -c "from complete_2048_bot import Complete2048Bot; print('✅ Bot ready')"

# Test browser engines
python3 test_cross_browser_compatibility.py
```

## Configuration

### Environment Variables
```bash
# Optional: Set browser preference
export BROWSER_TYPE="chromium"  # chromium, firefox, webkit

# Optional: Enable debug mode
export DEBUG_MODE="true"

# Optional: Set log level
export LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

### Bot Configuration
```python
from complete_2048_bot import Complete2048Bot

# Basic configuration
bot = Complete2048Bot(
    headless=False,    # Set to True for headless operation
    debug=True,        # Enable debug output
    log_level="INFO"   # Logging level
)

# Advanced configuration with custom strategy weights
bot.strategy.weights = {
    'empty_tiles': 150.0,
    'merge_potential': 100.0,
    'corner_bonus': 250.0,
    'monotonicity': 75.0,
    'max_tile_value': 15.0
}
```

## Usage Examples

### Basic Autonomous Game
```python
from complete_2048_bot import Complete2048Bot

# Context manager ensures proper cleanup
with Complete2048Bot(headless=False, debug=True) as bot:
    # Connect to game
    if bot.connect_to_game():
        # Play autonomous game
        results = bot.play_autonomous_game(max_moves=100)
        print(f"Game completed: {results}")
```

### Performance Testing
```python
# Run performance validation
bot = Complete2048Bot(headless=False, debug=True)
try:
    bot.connect_to_game()
    results = bot.play_autonomous_game(max_moves=500)

    # Calculate efficiency
    efficiency = results['final_score'] / results['moves_completed']
    print(f"Efficiency: {efficiency:.2f} points/move")
finally:
    bot.cleanup()
```

### Strategy Comparison
```python
from weight_tuning_framework import WeightTuningFramework

# Compare different strategy configurations
framework = WeightTuningFramework()
results = framework.run_weight_comparison(max_moves_per_test=50)
```

### Cross-Browser Testing
```python
from test_cross_browser_compatibility import run_comprehensive_browser_test

# Test all browser engines
results = run_comprehensive_browser_test()
for result in results:
    print(f"{result['browser']}: {result['status']}")
```

## Architecture Overview

### Core Components

1. **Playwright Controller** (`core/playwright_controller.py`)
   - Browser automation and control
   - Cross-browser compatibility (Chromium, Firefox, WebKit)
   - Ad blocking and page optimization

2. **Computer Vision System** (`core/canonical_vision.py`)
   - Real-time board state analysis
   - 100% accuracy tile recognition
   - Canonical color-based detection

3. **Strategy Engine** (`core/strategy.py`)
   - Heuristic-based move evaluation
   - Optimized weight configuration
   - Corner strategy and monotonicity analysis

4. **Error Handler** (`production_error_handler.py`)
   - Comprehensive error recovery
   - Logging and monitoring
   - Graceful failure handling

### Data Flow
```
Browser → Screenshot → Vision Analysis → Board State → Strategy → Move Decision → Browser Action
```

### Integration Points

- **Game URLs**: Primary (2048game.com) with fallbacks
- **Screenshot Pipeline**: PNG capture → OpenCV analysis
- **Move Execution**: Keyboard simulation via Playwright
- **State Tracking**: Real-time game state monitoring

## Production Deployment

### Headless Operation
```python
# Production bot without GUI
bot = Complete2048Bot(
    headless=True,
    debug=False,
    log_level="WARNING"
)
```

### Continuous Operation
```python
import time
from complete_2048_bot import Complete2048Bot

def run_continuous_games(num_games=10):
    results = []

    for game_num in range(num_games):
        with Complete2048Bot(headless=True, log_level="INFO") as bot:
            try:
                if bot.connect_to_game():
                    result = bot.play_autonomous_game(max_moves=200)
                    results.append(result)

                    # Cool-down between games
                    time.sleep(5)

            except Exception as e:
                bot.error_handler.handle_error(e, f"Game {game_num + 1}")

    return results
```

### Docker Deployment
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget curl gnupg \
    && rm -rf /var/lib/apt/lists/*

# Setup application
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install --with-deps chromium

COPY . .
CMD ["python3", "complete_2048_bot.py"]
```

## Troubleshooting

### Common Issues

#### Connection Problems
**Symptom**: "Connection failed" or timeout errors
**Solutions**:
1. Check internet connectivity
2. Try alternative URLs: `bot.connect_to_game("https://gabrielecirulli.github.io/2048/")`
3. Disable ad blocking: `PlaywrightController(block_ads=False)`
4. Check firewall settings

#### Vision System Issues
**Symptom**: "Board analysis failed" or incorrect tile detection
**Solutions**:
1. Update browser to latest version
2. Check screenshot quality in debug mode
3. Verify display scaling (100% recommended)
4. Clear browser cache

#### Performance Issues
**Symptom**: Slow execution or high resource usage
**Solutions**:
1. Enable headless mode: `headless=True`
2. Reduce max_moves limit
3. Close unnecessary applications
4. Use Chromium browser for better performance

#### Strategy Problems
**Symptom**: Poor move decisions or low scores
**Solutions**:
1. Verify strategy weights are optimized
2. Test with `test_enhanced_strategy.py`
3. Check for board state analysis errors
4. Review move history logs

### Debug Mode

Enable comprehensive debugging:
```python
bot = Complete2048Bot(debug=True, log_level="DEBUG")
```

Debug artifacts:
- Screenshot files: `bot_move_XXX_before.png`, `bot_move_XXX_after.png`
- Log files: `logs/2048_bot_TIMESTAMP.log`
- Error reports: Detailed traceback in logs

### Log Analysis

Check log files for issues:
```bash
# View recent logs
tail -f logs/2048_bot_*.log

# Search for errors
grep "ERROR" logs/2048_bot_*.log

# Monitor performance
grep "efficiency" logs/2048_bot_*.log
```

## Performance Tuning

### Browser Optimization
```python
# Optimal browser settings
controller = PlaywrightController(
    browser_type="chromium",  # Fastest engine
    headless=True,           # Reduce resource usage
    block_ads=True          # Improve loading speed
)
```

### Strategy Optimization
```python
# Performance-tuned weights
bot.strategy.weights = {
    'empty_tiles': 150.0,     # Higher for faster games
    'merge_potential': 100.0, # Prioritize merges
    'corner_bonus': 250.0,    # Maintain structure
    'monotonicity': 75.0,     # Improved flow
    'max_tile_value': 15.0    # Value progression
}
```

### Memory Management
```python
# Clean up between games
bot.cleanup()

# Limit screenshot retention
bot.debug = False  # Disable screenshot saving
```

## API Reference

### Complete2048Bot Class

#### Constructor
```python
Complete2048Bot(headless=False, debug=True, log_level="INFO")
```

#### Methods

**connect_to_game(url="https://2048game.com/") -> bool**
- Connects to 2048 game with fallback URLs
- Returns True if successful

**play_autonomous_game(max_moves=100) -> dict**
- Plays complete autonomous game
- Returns game statistics and results

**analyze_current_state() -> dict**
- Analyzes current board state
- Returns vision analysis results

**cleanup()**
- Cleans up resources and temporary files
- Called automatically in context manager

#### Properties

**strategy**: Access to strategy configuration
**error_handler**: Production error handling system
**move_count**: Current move number
**score**: Current game score

### Error Handler

**ProductionErrorHandler(log_level="INFO", enable_recovery=True)**
- Comprehensive error handling and logging
- Automatic recovery attempts
- Performance monitoring

### Testing Utilities

**test_cross_browser_compatibility.py**: Cross-browser testing
**weight_tuning_framework.py**: Strategy optimization
**run_visible_bot.py**: Performance validation

## Support

### Getting Help

1. Check this integration guide
2. Review troubleshooting section
3. Check log files for detailed errors
4. Run diagnostic tests:
   ```bash
   python3 test_cross_browser_compatibility.py
   python3 test_enhanced_strategy.py
   ```

### Contributing

For issues or improvements:
1. Check existing documentation
2. Create minimal reproduction case
3. Include system information and logs
4. Follow coding standards from existing codebase

### Version Information

- Bot Version: 2.0 (Production Ready)
- Compatible with: 2048game.com, gabrielecirulli.github.io/2048
- Browser Support: Chromium, Firefox, WebKit
- Python Support: 3.8+

---

**Note**: This bot is designed for educational purposes and demonstrates advanced browser automation, computer vision, and AI strategy techniques. Use responsibly and in accordance with game website terms of service.