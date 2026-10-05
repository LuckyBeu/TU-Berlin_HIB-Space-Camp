"""Station definitions for the Space Camp game.

Each station represents one task. Modes:
  - "task":    press the expected glove button(s).
  - "docking": run the docking minigame on the Pico.
"""


class Station:
    def __init__(self, name, audio_track, expected_buttons=None,
                 mode="task", duration=None):
        """
        Args:
            name: human-readable station name (for logs/debugging).
            audio_track: key of the intro audio clip to play.
            expected_buttons: list of button names (for mode="task").
            mode: "task" or "docking".
            duration: minigame duration in seconds (for mode="docking").
        """
        self.name = name
        self.audio_track = audio_track
        self.expected_buttons = expected_buttons or []
        self.mode = mode
        self.duration = duration
        self.completed = False

    def validate_input(self, pressed_buttons):
        """Return True if exactly the expected buttons were pressed."""
        if set(pressed_buttons) == set(self.expected_buttons):
            self.completed = True
            return True
        return False

    @property
    def expected_leds(self):
        """LED names corresponding to the expected buttons."""
        return [b.replace("button", "led") for b in self.expected_buttons]

    def __repr__(self):
        return "Station(name={!r}, track={!r}, mode={!r})".format(
            self.name, self.audio_track, self.mode)


def create_stations():
    """Define the sequence of stations (tasks) for one game run."""
    return [
        Station("Launch Pad", "exercise_1", ["button1"]),                 # index finger
        Station("Docking",    "exercise_2", mode="docking", duration=60),  # minigame
        Station("Landing",    "exercise_3", ["button1", "button3"]),       # index + middle
    ]