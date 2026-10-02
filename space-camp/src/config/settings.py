# Configuration settings for the Space Camp game

# Audio track file paths
AUDIO_TRACKS = {
    "intro": "assets/audio/intro.wav",              # played at game start
    "exercise_1": "assets/audio/exercise_1.wav",    # before start task 1
    "exercise_2": "assets/audio/exercise_2.wav",    # before start task 2
    "exercise_3": "assets/audio/exercise_3.wav",    # before start task 3
    "game_over": "assets/audio/game_over.wav",      # on failure
    "congrats": "assets/audio/congrats.wav",        # game won
}

# Timing settings
COUNTDOWN_TIME = 30  # Time in seconds for each task
BUTTON_DEBOUNCE_TIME = 0.2  # Debounce time in seconds for button presses

# GPIO pin settings
BUTTON_PINS = {
    "button1": 17,
    "button2": 27,
    "button3": 22,
}