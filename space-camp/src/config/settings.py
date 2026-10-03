# Configuration settings for the Space Camp game

import os

# Project root, resolved relative to this file so paths work from any CWD
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIO_DIR = os.path.join(PROJECT_ROOT, "assets", "audio")

# Audio track file paths
AUDIO_TRACKS = {
    "intro": os.path.join(AUDIO_DIR, "intro.wav"),                      # played at game start
    "exercise_1": os.path.join(AUDIO_DIR, "exercise_1.wav"),            # before start task 1
    "exercise_2": os.path.join(AUDIO_DIR, "exercise_2.wav"),            # before start task 2
    "exercise_3": os.path.join(AUDIO_DIR, "exercise_3.wav"),            # before start task 3
    "game_over": os.path.join(AUDIO_DIR, "game_over.wav"),              # game over
    "congrats": os.path.join(AUDIO_DIR, "congrats.wav"),                # game won
    "background": os.path.join(AUDIO_DIR, "helicopter-on-mars.wav"),    # background noise
}

# Timing settings
COUNTDOWN_TIME = 10  # Time in seconds for each task
BUTTON_DEBOUNCE_TIME = 0.2  # Debounce time in seconds for button presses

# GPIO pin settings
BUTTON_PINS = {
    "button1": 17, # index finger
    "button2": 27, # middle finger
    "button3": 22, # ring finger
    "button4": 10, # pinky finger
}

LED_PINS = {
    "led1": 14, # index finger
    "led2": 15, # middle finger
    "led3": 18, # ring finger
    "led4": 23, # pinky finger
}