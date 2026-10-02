# Space Camp Game

## Overview
Space Camp is an interactive game designed for the Raspberry Pi Model 3B+, where users interact with a glove equipped with buttons on the fingertips. The game involves completing various tasks while audio tracks play at different stages, enhancing the immersive experience.

## Features
- User interaction through a glove with fingertip buttons.
- Audio tracks that play during gameplay to provide feedback and enhance the experience.
- Countdown timer for each task to add urgency.
- Visual feedback through an LED matrix (if applicable).
- Haptic feedback through the glove for an immersive experience.

## Project Structure
```
space-camp
├── src
│   ├── main.py
│   ├── game
│   │   ├── __init__.py
│   │   ├── game_loop.py
│   │   ├── countdown.py
│   │   └── stations.py
│   ├── hardware
│   │   ├── __init__.py
│   │   ├── glove.py
│   │   ├── buttons.py
│   │   ├── led_matrix.py
│   │   └── force_feedback.py
│   ├── audio
│   │   ├── __init__.py
│   │   └── audio_player.py
│   └── config
│       ├── __init__.py
│       └── settings.py
├── assets
│   └── audio
│       └── tracks.md
├── tests
│   ├── test_glove.py
│   ├── test_game_loop.py
│   └── test_audio_player.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup Instructions
1. **Hardware Setup**: Connect the glove to the Raspberry Pi GPIO pins as per the hardware specifications.
2. **Install Dependencies**: Run `pip install -r requirements.txt` to install the necessary libraries.
3. **Run the Game**: Execute `python src/main.py` to start the game.

## Gameplay
Players will use the glove to complete various tasks while audio tracks play in the background. The game will provide feedback through audio, visual cues, and haptic responses to enhance the user experience.

## Future Enhancements
- Additional audio tracks and sound effects.
- More complex tasks and challenges.
- Improved visual feedback through the LED matrix.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.