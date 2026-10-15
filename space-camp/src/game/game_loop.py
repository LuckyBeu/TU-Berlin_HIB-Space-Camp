import time

from game.stations import create_stations


class GameLoop:
    def __init__(self, glove, audio_player, countdown_time, debounce_time,
                 countdown_server=None, stations=None,
                 finger_yoga_time=None, kabelsalat_time=None):
        self.glove = glove
        self.audio = audio_player
        self.countdown_time = countdown_time
        self.debounce_time = debounce_time
        self.countdown_server = countdown_server   # drives the Pico display
        # Whole-game time budgets (fall back to countdown_time if unset)
        self.finger_yoga_time = (finger_yoga_time
                                 if finger_yoga_time is not None else countdown_time)
        self.kabelsalat_time = (kabelsalat_time
                                if kabelsalat_time is not None else countdown_time)

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

        if station.mode == "kabelsalat":
            duration_s = self.kabelsalat_time
        else:
            duration_s = (station.duration or self.countdown_time)
        self.countdown_server.start_game(station.mode)
        # Docking occupies the countdown display (rocket Pico) itself; for
        # Kabelsalat that display is free, so show the countdown there.
        show_countdown = station.mode != "docking"
        if show_countdown:
            self.countdown_server.start(duration_s)
        try:
            result = self.countdown_server.wait_for_result(timeout=duration_s + 10)
        finally:
            if show_countdown:
                self.countdown_server.reset()

        if result is None:
            print("Minigame '{}' timed out.".format(station.mode))
            return False
        return result

    def run_finger_yoga(self, station):
        """Play the finger-yoga sequence within one shared time budget.

        The whole sequence must be completed within finger_yoga_time seconds
        (not per button). Returns True if completed in time, else False.
        """
        if self.countdown_server:
            self.countdown_server.start(self.finger_yoga_time)

        deadline = time.time() + self.finger_yoga_time
        try:
            for step, button in enumerate(station.sequence, start=1):
                led = button.replace("button", "led")
                print("Finger Yoga step {}/{}: press {}".format(
                    step, len(station.sequence), button))

                self.glove.all_leds_off()
                self.glove.set_led(led, True)

                success = self._wait_for_single_button(button, deadline)

                self.glove.all_leds_off()
                if not success:
                    return False
            return True
        finally:
            if self.countdown_server:
                self.countdown_server.reset()

    def _wait_for_single_button(self, expected_button, deadline):
        """Wait for a single correct button press until the shared deadline.

        Returns True on the correct button, False on wrong button or timeout.
        """
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