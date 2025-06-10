# Endless Jumper - Enhanced Edition

A dynamic endless jumping game built with Pygame where you climb ever-higher while collecting power-ups and facing increasing difficulty.

## Features

- **Dynamic Difficulty Scaling**: Platforms get smaller and more spread out as you climb higher
- **Power-up System**: Multiple power-ups to collect:
  - Double Jump: Gain ability to jump in mid-air
  - Big Platforms: Temporarily increases platform sizes
  - Slow Motion: Temporarily slows down game physics
- **Visual Effects**: Player trail effects and platform color coding
- **Score System**: High score tracking with persistent storage
- **Game Statistics**: Track jumps, power-ups collected, and play time
- **Pause Functionality**: Pause the game at any time

## Controls

- Left/Right Arrow Keys: Move horizontally
- Up Arrow Key: Use double jump (when available)
- P: Pause/Unpause game
- R: Restart game (when game over)

## Installation

1. Ensure you have Python installed on your system
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## Game Mechanics

- **Platform Generation**: Platforms are procedurally generated with increasing difficulty
- **Screen Wrapping**: Player can move off one side of the screen and appear on the other
- **Fall Protection**: Game ends if player falls too far without landing
- **Difficulty Progression**:
  - Platform width decreases with height
  - Gaps between platforms increase
  - Platform count reduces at higher levels
  - More extreme horizontal spacing at higher scores


## Technical Details

- Built with Pygame
- Object-oriented design with separate classes for:
  - Game: Main game loop and state management
  - Player: Player physics and power-up states
  - Platform: Platform behavior and visual effects
  - PowerUp: Power-up types and effects
- Persistent high score system using JSON storage
- Configurable game constants for easy tweaking
- Extensive unit testing coverage

## Game Constants

- Screen Size: 800x600 pixels
- Base Platform Width: 200 pixels
- Minimum Platform Width: 90 pixels
- Maximum Fall Speed: 20 pixels/frame
- Maximum Fall Distance: 400 pixels