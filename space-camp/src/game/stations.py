"""Station definitions for the Space Camp game.

Modes:
  - "finger_yoga": press a random sequence of glove buttons (runs on the Pi).
  - "kabelsalat":  cable-wiring minigame (runs on the Kabelsalat Pico).
  - "docking":     docking minigame (runs on the countdown/rocket Pico).
"""

import random


def generate_button_sequence(buttons, length=10, max_repeat=2):
    """Generate a random button sequence.

    Ensures the same button never appears more than `max_repeat` times
    in a row.

    Args:
        buttons: list of available button names, e.g. ["button1", ...].
        length: number of steps in the sequence.
        max_repeat: max allowed consecutive repeats of the same button.
    Returns:
        A list of button names of the given length.
    """
    sequence = []
    for _ in range(length):
        choices = list(buttons)
        # Forbid a button that would exceed max_repeat consecutive uses
        if len(sequence) >= max_repeat:
            tail = sequence[-max_repeat:]
            if len(set(tail)) == 1:  # last `max_repeat` are identical
                choices = [b for b in buttons if b != tail[-1]]
        sequence.append(random.choice(choices))
    return sequence


class Station:
    def __init__(self, name, audio_track, expected_buttons=None,
                 mode="finger_yoga", duration=None, sequence=None):
        self.name = name
        self.audio_track = audio_track
        self.expected_buttons = expected_buttons or []
        self.mode = mode
        self.duration = duration
        self.sequence = sequence or []
        self.completed = False

    def validate_input(self, pressed_buttons):
        """For combo tasks: True if exactly the expected buttons were pressed."""
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


def create_stations(buttons=None):
    """Define the sequence of stations (tasks) for one game run.

    Args:
        buttons: list of available button names for the finger-yoga sequence.
    """
    buttons = buttons or ["button1", "button2", "button3", "button4"]
    yoga_sequence = generate_button_sequence(buttons, length=10, max_repeat=2)

    return [
        Station("Finger Yoga", "exercise_1", mode="finger_yoga",
                sequence=yoga_sequence),
        Station("Kabelsalat", "exercise_2", mode="kabelsalat", duration=120),
        Station("Docking", "exercise_3", mode="docking", duration=60),
    ]
