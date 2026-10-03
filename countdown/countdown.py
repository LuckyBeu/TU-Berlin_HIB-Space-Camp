"""Countdown logic and rendering for the 32x8 matrix.

Displays remaining time as SS:cc (seconds : centiseconds / hundredths).
Layout mirrors the led-counter: two 2-digit groups separated by ':' dots.
"""
import time
import config


class Countdown:
    def __init__(self, display):
        self.display = display
        self.state = config.STATE_IDLE
        self.remaining_ms = 0          # time left in milliseconds
        self._tick_ref = None          # ticks_ms reference while running
        self._blink_on = True
        self._last_blink = time.ticks_ms()

    # ----- command handling -------------------------------------------------
    def handle(self, cmd):
        if not cmd or "cmd" not in cmd:
            return
        action = cmd["cmd"]
        if action == "start":
            self.remaining_ms = max(0, int(cmd.get("ms", 0)))
            self.state = config.STATE_RUNNING
            self._tick_ref = time.ticks_ms()
        elif action == "pause":
            if self.state == config.STATE_RUNNING:
                self._accumulate()
                self.state = config.STATE_PAUSED
        elif action == "resume":
            if self.state == config.STATE_PAUSED:
                self.state = config.STATE_RUNNING
                self._tick_ref = time.ticks_ms()
        elif action == "sync":
            # correct drift against the Pi's authoritative clock
            self.remaining_ms = max(0, int(cmd.get("ms", self.remaining_ms)))
            self._tick_ref = time.ticks_ms()
        elif action == "reset":
            self.state = config.STATE_IDLE
            self.remaining_ms = 0
            self._tick_ref = None

    def _accumulate(self):
        """Subtract elapsed time since the last tick reference."""
        if self._tick_ref is not None:
            elapsed = time.ticks_diff(time.ticks_ms(), self._tick_ref)
            self.remaining_ms = max(0, self.remaining_ms - elapsed)
            self._tick_ref = time.ticks_ms()

    # ----- per-frame update -------------------------------------------------
    def update(self):
        if self.state == config.STATE_RUNNING:
            self._accumulate()
            if self.remaining_ms <= 0:
                self.remaining_ms = 0
                self.state = config.STATE_FINISHED
        self._render()

    # ----- rendering --------------------------------------------------------
    def _color_for_time(self):
        secs = self.remaining_ms / 1000.0
        if secs <= config.CRITICAL_THRESHOLD_S:
            return config.CRITICAL_COLOR
        if secs <= config.WARNING_THRESHOLD_S:
            return config.WARNING_COLOR
        return config.NORMAL_COLOR

    def _render(self):
        d = self.display
        d.clear()

        if self.state == config.STATE_IDLE:
            d.write()
            return

        # SS:cc  -> seconds and centiseconds (hundredths)
        total_ms = self.remaining_ms
        seconds = total_ms // 1000
        centis = (total_ms % 1000) // 10
        if seconds > 99:
            seconds = 99  # display clamps at 99 s

        # Blink the whole display when finished
        if self.state == config.STATE_FINISHED:
            now = time.ticks_ms()
            if time.ticks_diff(now, self._last_blink) >= 400:
                self._blink_on = not self._blink_on
                self._last_blink = now
            if not self._blink_on:
                d.write()
                return
            color = config.FINISHED_COLOR
        else:
            color = self._color_for_time()

        # Separator dots (colon) at x=16
        d.set_pixel(16, 1, config.SEPARATOR_COLOR)
        d.set_pixel(16, 2, config.SEPARATOR_COLOR)
        d.set_pixel(16, 4, config.SEPARATOR_COLOR)
        d.set_pixel(16, 5, config.SEPARATOR_COLOR)

        # Left group: seconds (positions match led-counter layout)
        d.draw_digit(seconds // 10, 4, 0, color)
        d.draw_digit(seconds % 10, 10, 0, color)

        # Right group: centiseconds
        d.draw_digit(centis // 10, 18, 0, color)
        d.draw_digit(centis % 10, 24, 0, color)

        d.write()