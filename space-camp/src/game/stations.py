"""Station definitions for the Space Camp game.

Modes:
  - "finger_yoga": press the expected glove buttons (runs on the Pi).
  - "kabelsalat":  cable-wiring minigame (runs on the Kabelsalat Pico).
  - "docking":     docking minigame (runs on the countdown/rocket Pico).
"""


class Station:
    def __init__(self, name, audio_track, expected_buttons=None,
                 mode="finger_yoga", duration=None):
        self.name = name
        self.audio_track = audio_track
        self.expected_buttons = expected_buttons or []
        self.mode = mode
        self.duration = duration
        self.completed = False

    def validate_input(self, pressed_buttons):
        if set(pressed_buttons) == set(self.expected_buttons):
            self.completed = True
            return True
        return False

    @property
    def expected_leds(self):
        return [b.replace("button", "led") for b in self.expected_buttons]

    def __repr__(self):
        return "Station(name={!r}, track={!r}, mode={!r})".format(
            self.name, self.audio_track, self.mode)


def create_stations():
    return [
        Station("Finger Yoga", "exercise_1", mode="finger_yoga",
                expected_buttons=["button1", "button2", "button3"]),
        Station("Kabelsalat", "exercise_2", mode="kabelsalat", duration=120),
        Station("Docking", "exercise_3", mode="docking", duration=60),
    ]


def run(duration=60):
    """Run one Kabelsalat round.

    Args:
        duration: time limit in seconds.
    Returns:
        True if the player connected all cables correctly in time,
        False otherwise.
    """
    # TODO: bestehende Spiellogik hier aufrufen / umhüllen.
    # Beispielgerüst:
    #   setup()
    #   success = play_round(time_limit=duration)
    #   cleanup()
    #   return success
    raise NotImplementedError("Kabelsalat run() muss an die Spiellogik angebunden werden")


"""Adapter to launch the Kabelsalat minigame from Space Camp."""

import sys
import os

# Pfad zum kabelsalat-Projekt (zwei Ebenen hoch aus src/game -> Repo-Root -> kabelsalat)
_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_KABELSALAT_DIR = os.path.join(_REPO_ROOT, "kabelsalat")
if _KABELSALAT_DIR not in sys.path:
    sys.path.insert(0, _KABELSALAT_DIR)


def run_kabelsalat(duration=60):
    """Run the Kabelsalat minigame. Returns True on success."""
    import game as kabelsalat_game  # kabelsalat/game.py
    return kabelsalat_game.run(duration=duration)


class Game:
    def __init__(self, stations, duration=60):
        self.stations = stations
        self.duration = duration

    def run(self):
        self.audio.start_loop("background")
        try:
            self.audio.play("intro")

            for station in self.stations:
                self.audio.play(station.audio_track)

                if station.mode == "finger_yoga":
                    success = self.wait_for_press(station)
                elif station.mode == "kabelsalat":
                    success = run_kabelsalat(duration=station.duration)
                elif station.mode == "docking":
                    success = self._run_docking(station)
                else:
                    success = self.wait_for_press(station)

                if not success:
                    self.audio.play("game_over")
                    return

            self.audio.play("congrats")
        finally:
            self.audio.stop_loop()
            self.glove.cleanup()