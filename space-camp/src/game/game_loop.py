import time


class GameLoop:
    def __init__(self, glove, audio_player, countdown_time, debounce_time):
        self.glove = glove
        self.audio = audio_player
        self.countdown_time = countdown_time
        self.debounce_time = debounce_time

        # Each task: the intro audio, and the expected button name
        self.tasks = [
            ("exercise_1", "button1"),  # index finger
            ("exercise_2", "button2"),  # middle finger
            ("exercise_3", "button3"),  # pinky finger
        ]

    def wait_for_press(self, expected_button):
        """Wait for a button press within the countdown time.
        Returns True if the correct button was pressed,
        False on wrong button or timeout."""
        deadline = time.time() + self.countdown_time
        while time.time() < deadline:
            buttons = self.glove.read_buttons()
            pressed = [name for name, state in buttons.items() if state]

            if pressed:
                # Debounce
                time.sleep(self.debounce_time)
                buttons = self.glove.read_buttons()
                pressed = [name for name, state in buttons.items() if state]

                if not pressed:
                    continue

                if pressed == [expected_button]:
                    return True
                else:
                    # Wrong finger (or multiple fingers)
                    return False

            time.sleep(0.01)

        # Timeout
        return False

    def run(self):
        try:
            # 1. Start -> intro
            self.audio.play("intro")

            # 2-4. Each task
            for intro_track, expected_button in self.tasks:
                self.audio.play(intro_track)

                success = self.wait_for_press(expected_button)
                if not success:
                    self.audio.play("game_over")
                    return

            # All tasks solved
            self.audio.play("congrats")

        finally:
            self.glove.cleanup()