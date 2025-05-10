# Slither.io Bot

An automated bot that plays Slither.io using Selenium WebDriver. The bot uses computer vision and game state analysis to navigate the game, collect food, and avoid other snakes.

## Features

- Automated gameplay using Selenium WebDriver
- Intelligent food collection with blacklisting system
- Enemy snake avoidance with danger detection
- Visual overlay showing bot's decision-making process
- Performance tracking (lifespan, food collected, etc.)
- Panic mode for emergency situations

## Prerequisites

- Python 3.x
- Chrome browser installed
- ChromeDriver (matching your Chrome version)

## Installation

1. Clone this repository
2. Install required Python packages:
```bash
pip install selenium
```
3. Download ChromeDriver:
   - Visit [ChromeDriver downloads](https://sites.google.com/chromium.org/driver/)
   - Download the version matching your Chrome browser
   - Place `chromedriver.exe` in the project directory

## Usage

1. Run the bot:
```bash
python main.py
```

2. The bot will:
   - Open Slither.io in Chrome
   - Enter the game with the nickname "PythonBot"
   - Start playing automatically
   - Display performance metrics when the game ends

## How It Works

The bot uses several key strategies:

1. **Food Collection**:
   - Targets the nearest food particles
   - Implements a blacklisting system to avoid getting stuck
   - Tracks food collection statistics

2. **Enemy Avoidance**:
   - Detects nearby enemy snakes
   - Calculates repulsion vectors to avoid collisions
   - Activates panic mode (speed boost) when in immediate danger

3. **Visual Feedback**:
   - Overlay shows:
     - Danger zones (red)
     - Panic zones (orange)
     - Movement vectors (blue for attraction, red for repulsion)
     - Enemy snake positions

## Performance Metrics

The bot tracks:
- Game lifespan
- Final snake size
- Total food collected
- Number of food blacklist events

## Notes

- The bot uses a combination of attraction and repulsion forces to navigate
- It automatically activates speed boost when in danger
- The visual overlay helps understand the bot's decision-making process
- The bot will automatically close the browser when the game ends

## Disclaimer

This bot is for educational purposes only. Using bots in online games may violate the game's terms of service.