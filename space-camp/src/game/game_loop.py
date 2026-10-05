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

    def run(self):
        try:
            self.audio.start_loop("background")
            self.audio.play("intro")

            for station in self.stations:
                print("Starting station:", station.name)
                self.audio.play(station.audio_track)

                # Light the LEDs for the fingers that must be pressed
                self.glove.set_leds(station.expected_leds, on=True)

                success = self.wait_for_press(station)

                self.glove.all_leds_off()

                if not success:
                    self.audio.play("game_over")
                    return

            # All stations solved
            self.audio.play("congrats")

        finally:
            self.audio.stop_loop()
            self.glove.all_leds_off()
            self.glove.cleanup()