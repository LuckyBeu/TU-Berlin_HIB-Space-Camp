import time


class GameLoop:
    def __init__(self, glove, audio_player, countdown_time, debounce_time):
        self.glove = glove
        self.audio = audio_player
        self.countdown_time = countdown_time
        self.debounce_time = debounce_time

        # Each task: the intro audio, and the expected button name(s)
        self.tasks = [
            ("exercise_1", ["button1"]),             # index finger
            ("exercise_2", ["button2", "button4"]),  # middle + pinky finger
            ("exercise_3", ["button1", "button3"]),  # index + middle together
        ]

    def wait_for_press(self, expected_buttons):
        """Wait for a button press within the countdown time.
        Returns True if exactly the expected button(s) were pressed,
        False on wrong button(s) or timeout."""
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

                print(f"Button pressed: {', '.join(pressed)}")

                if set(pressed) == set(expected_buttons):
                    return True
                else:
                    # Wrong finger(s)
                    return False

            time.sleep(0.01)

        # Timeout
        return False

    def run(self):
        try:
            # Background ambience loops for the whole game
            self.audio.start_loop("background")

            # 1. Start -> intro
            self.audio.play("intro")

            # 2-4. Each task
            for intro_track, expected_buttons in self.tasks:

                self.audio.play(intro_track)

                # Light the LEDs for the fingers that must be pressed
                expected_leds = [b.replace("button", "led") for b in expected_buttons]
                self.glove.set_leds(expected_leds, on=True)

                success = self.wait_for_press(expected_buttons)

                self.glove.all_leds_off()

                if not success:
                    self.audio.play("game_over")
                    return

            # All tasks solved
            self.audio.play("congrats")

        finally:
            self.audio.stop_loop()
            self.glove.all_leds_off()
            self.glove.cleanup()