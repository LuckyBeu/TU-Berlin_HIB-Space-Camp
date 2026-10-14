import time

from game.stations import create_stations


class GameLoop:
    def __init__(self, glove, audio_player, countdown_time, debounce_time,
                 countdown_server=None, stations=None):
        self.glove = glove
        self.audio = audio_player
        self.countdown_time = countdown_time
        self.debounce_time = debounce_time
        self.countdown_server = countdown_server   # drives the Pico display

        # Stations define the tasks; injectable for easy testing/variation
        self.stations = stations if stations is not None else create_stations()

    def wait_for_press(self, station):
        """Wait for a button press within the countdown time.

        Returns True if exactly the station's expected button(s) were
        pressed, False on wrong button(s) or timeout.
        """
        if self.countdown_server:
            self.countdown_server.start(self.countdown_time)

        deadline = time.time() + self.countdown_time
        try:
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

                    print("Button pressed: {}".format(", ".join(pressed)))
                    return station.validate_input(pressed)

                time.sleep(0.01)

            return False  # timeout
        finally:
            if self.countdown_server:
                self.countdown_server.reset()

    def run_minigame(self, station):
        """Start a Pico-based minigame and wait for its result.

        Mirrors the docking flow for both 'docking' and 'kabelsalat'.
        """
        if not self.countdown_server:
            print("No countdown_server configured; cannot run minigame.")
            return False

        duration_s = (station.duration or self.countdown_time)
        self.countdown_server.start_game(station.mode)
        result = self.countdown_server.wait_for_result(timeout=duration_s + 10)

        if result is None:
            print("Minigame '{}' timed out.".format(station.mode))
            return False
        return result

    def run_finger_yoga(self, station):
        """Play the finger-yoga sequence.

        For each button in station.sequence, light its LED and wait for the
        player to press exactly that button within the countdown time.
        Returns True if the whole sequence is completed, else False.
        """
        for step, button in enumerate(station.sequence, start=1):
            led = button.replace("button", "led")
            print("Finger Yoga step {}/{}: press {}".format(
                step, len(station.sequence), button))

            self.glove.all_leds_off()
            self.glove.set_led(led, True)

            success = self._wait_for_single_button(button)

            self.glove.all_leds_off()
            if not success:
                return False
        return True

    def _wait_for_single_button(self, expected_button):
        """Wait for a single correct button press within countdown_time.

        Returns True on the correct button, False on wrong button or timeout.
        """
        deadline = time.time() + self.countdown_time
        while time.time() < deadline:
            buttons = self.glove.read_buttons()
            pressed = [name for name, state in buttons.items() if state]

            if pressed:
                time.sleep(self.debounce_time)
                buttons = self.glove.read_buttons()
                pressed = [name for name, state in buttons.items() if state]
                if not pressed:
                    continue

                if pressed == [expected_button]:
                    print("Button pressed:", expected_button)
                    # wait for release to avoid double-counting
                    while any(self.glove.read_buttons().values()):
                        time.sleep(0.01)
                    return True
                else:
                    print("Wrong button(s):", pressed)
                    return False

            time.sleep(0.01)

        print("Timeout waiting for", expected_button)
        return False

    def run(self):
        try:
            self.audio.start_loop("background")
            self.audio.play("intro")

            for station in self.stations:
                print("Starting station:", station.name)
                self.audio.play(station.audio_track)

                if station.mode in ("docking", "kabelsalat"):
                    success = self.run_minigame(station)
                elif station.mode == "finger_yoga":
                    success = self.run_finger_yoga(station)
                else:
                    self.glove.set_leds(station.expected_leds, on=True)
                    success = self.wait_for_press(station)
                    self.glove.all_leds_off()

                if not success:
                    self.audio.play("game_over")
                    return

            self.audio.play("congrats")

        finally:
            self.audio.stop_loop()
            self.glove.all_leds_off()
            self.glove.cleanup()