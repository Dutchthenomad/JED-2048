# Installation Guide

Complete setup instructions for the JED-2048 Educational Platform.

## 🚀 Quick Start (Recommended)

```bash
git clone https://github.com/Dutchthenomad/JED-2048.git
cd JED-2048
make setup
make run
```

That's it! The bot should open a browser and start playing 2048.

## 📋 Detailed Installation

### Prerequisites

- **Python 3.8+** (3.12 recommended)
- **Git** for repository management
- **Modern Browser** (Chromium, Firefox, or Safari)
- **Internet Connection** for initial setup

### Step 1: Clone Repository

```bash
git clone https://github.com/Dutchthenomad/JED-2048.git
cd JED-2048
```

### Step 2: Environment Setup

The Makefile handles everything automatically:

```bash
make setup
```

This command:
- Creates a Python virtual environment (`.venv`)
- Installs all dependencies from `requirements.txt`
- Downloads Playwright browsers (Chromium, Firefox, WebKit)
- Verifies the installation

### Step 3: Verify Installation

```bash
# Test the bot with visible browser
make run

# Run a quick 16-move demonstration
make run16

# Run test suite (optional)
make test
```

## 🔧 Manual Installation

If you prefer manual setup or encounter issues:

### 1. Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Dependencies

```bash
pip install -r requirements.txt
```

### 3. Playwright Browsers

```bash
playwright install
```

### 4. Verification

```bash
python run_visible_bot.py
```

## 🛠️ Troubleshooting

### Common Issues

**1. Playwright Installation Fails**
```bash
# Try manual installation
pip install playwright
playwright install chromium
```

**2. Python Version Issues**
```bash
# Check version
python3 --version

# Must be 3.8 or higher
```

**3. Browser Launch Fails**
```bash
# Test browser installation
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

**4. Permission Issues on Linux**
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip
```

### System-Specific Setup

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip git
```

**macOS:**
```bash
# Install Homebrew first (if needed)
brew install python3 git
```

**Windows:**
```bash
# Use Windows Subsystem for Linux (recommended)
# Or install Python from python.org
```

### Performance Optimization

**For slower systems:**
```bash
# Use headless mode for better performance
python enhanced_2048_bot.py --headless
```

**For development:**
```bash
# Enable debug mode
python enhanced_2048_bot.py --debug
```

## 📊 Verification Tests

Run these commands to ensure everything works:

### 1. Core Functionality
```bash
python -c "
from core.vision import BoardVision
from core.strategy import BasicStrategy
print('✓ Core modules loaded')
"
```

### 2. Algorithm Framework
```bash
python -c "
from algorithms.algorithm_manager import AlgorithmManager
manager = AlgorithmManager()
print(f'✓ Found {len(manager.get_available_algorithms())} algorithms')
"
```

### 3. Browser Automation
```bash
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    browser.close()
print('✓ Browser automation working')
"
```

### 4. Educational Platform
```bash
python -c "
from student_platform import StudentPlatform
from leaderboard_system import LeaderboardSystem
print('✓ Educational platform ready')
"
```

## 🎓 Development Setup

For contributors and advanced users:

### 1. Development Dependencies
```bash
pip install black isort mypy pytest-cov
```

### 2. Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

### 3. IDE Configuration
```bash
# VS Code settings (optional)
mkdir .vscode
echo '{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.linting.enabled": true,
  "python.formatting.provider": "black"
}' > .vscode/settings.json
```

## 📱 Alternative Configurations

### Headless Mode (No GUI)
```bash
export PLAYWRIGHT_HEADLESS=true
python enhanced_2048_bot.py
```

### Different Browsers
```bash
# Firefox
python enhanced_2048_bot.py --browser firefox

# WebKit (Safari engine)
python enhanced_2048_bot.py --browser webkit
```

### Custom Game URLs
```bash
python enhanced_2048_bot.py --url "https://play2048.co/"
```

## 🆘 Getting Help

1. **Check Documentation**: `docs/` directory
2. **Common Issues**: `TROUBLESHOOTING.md`
3. **GitHub Issues**: Report bugs and ask questions
4. **Community**: Join discussions for help and tips

---

**Installation Complete!** You're ready to explore AI-powered 2048 gameplay and start developing your own algorithms.

*JED-2048 Educational Platform*