"""Kabelsalat wiring minigame for the Pico 2 W.

Hardware model (common-anode LEDs, cathode -> GPIO, "schalten nach Masse"):
  - Upper row cathodes: LED_1_1..LED_1_5 -> drive the pin LOW to light the LED,
    set it to high-Z (input) to switch it off.
  - Lower row cathodes: LED_2_1..LED_2_5 -> never driven by the Pico. A lower
    LED lights passively once the player patches its socket to an upper socket
    that is currently held LOW (ground flows through the cable). The Pico only
    reads these pins (input + pull-up) to detect the connection.

Gameplay:
  A hidden permutation maps each lower LED to one upper LED. One upper LED
  lights up at a time (the newest one blinks); the player patches the matching
  lower socket to it. When the correct lower LED lights (grounded through the
  cable), that step is locked in and the next upper LED lights up. Wiring all
  five correctly wins the round.
"""
import time
import random

from machine import Pin

import config


class Kabelsalat:
    def __init__(self, listener=None):
        """listener: optional UdpListener so the game keeps draining packets
        and can abort on a 'reset' command."""
        self.listener = listener
        self.n = config.KABEL_LED_COUNT

        self.upper = [Pin(p, Pin.IN) for p in (
            config.LED_1_1, config.LED_1_2, config.LED_1_3,
            config.LED_1_4, config.LED_1_5)][:self.n]
        # lower pins stay inputs with pull-ups for the whole game (sense only)
        self.lower = [Pin(p, Pin.IN, Pin.PULL_UP) for p in (
            config.LED_2_1, config.LED_2_2, config.LED_2_3,
            config.LED_2_4, config.LED_2_5)][:self.n]

        self.target = list(range(self.n))  # lower index -> upper index
        self.progress = 0

    # -- low level pin control ---------------------------------------------
    def _drive_low(self, idx):
        """Pull the given upper pin LOW so its LED lights (sinks to ground)."""
        self.upper[idx].init(Pin.OUT)
        self.upper[idx].value(0)

    def _release(self, idx):
        """Switch the given upper pin to high-Z (input) so its LED turns off."""
        self.upper[idx].init(Pin.IN)  # high-Z -> LED off

    def _all_off(self):
        """Release every upper pin, turning the whole upper row off."""
        for i in range(self.n):
            self._release(i)

    # -- setup --------------------------------------------------------------
    def _shuffle_targets(self):
        """Return a random lower->upper permutation with at least one crossing."""
        t = list(range(self.n))
        for i in range(self.n - 1, 0, -1):
            j = random.randint(0, i)
            t[i], t[j] = t[j], t[i]
        # force at least one crossing so it is a real "Kabelsalat"
        if all(t[i] == i for i in range(self.n)):
            t[0], t[1] = t[1], t[0]
        return t

    def _new_game(self):
        """Reset state for a fresh round: new wiring puzzle, zero progress."""
        self.target = self._shuffle_targets()
        self.progress = 0
        self._all_off()

    # -- display ------------------------------------------------------------
    def _apply_display(self, blink_on):
        """Light the completed upper targets (solid) plus the current one
        (blinking). Everything else is off."""
        for i in range(self.n):
            self._release(i)
        for step in range(self.progress):
            self._drive_low(self.target[step])
        if self.progress < self.n and blink_on:
            self._drive_low(self.target[self.progress])

    # -- sensing ------------------------------------------------------------
    def _sense_current(self):
        """True when the current lower socket is patched to the current upper
        target. Only the current target is driven LOW during the read so a
        cable to an already-completed target can't cause a false hit."""
        t = self.target[self.progress]
        for i in range(self.n):
            self._release(i)
        self.upper[t].init(Pin.OUT)
        self.upper[t].value(0)
        time.sleep_us(config.KABEL_SENSE_SETTLE_US)
        return self.lower[self.progress].value() == 0

    # -- feedback -----------------------------------------------------------
    def _win_animation(self):
        for _ in range(4):
            for i in range(self.n):
                self._drive_low(self.target[i])
            time.sleep_ms(150)
            self._all_off()
            time.sleep_ms(120)
        self._all_off()

    # -- main loop ----------------------------------------------------------
    def run(self):
        """Run one round. Returns True on success, False on reset/timeout."""
        self._new_game()

        start = time.ticks_ms()
        last_frame = start
        last_blink = start
        blink_on = True
        stable_since = None

        while True:
            now = time.ticks_ms()

            if self.listener is not None:
                cmd = self.listener.poll()
                if cmd and cmd.get("cmd") == "reset":
                    self._all_off()
                    return False

            if time.ticks_diff(now, last_frame) < config.KABEL_FRAME_MS:
                time.sleep_ms(2)
                continue
            last_frame = now

            if time.ticks_diff(now, last_blink) >= config.KABEL_BLINK_MS:
                last_blink = now
                blink_on = not blink_on
            self._apply_display(blink_on)

            hit = self._sense_current()
            self._apply_display(blink_on)  # restore after the sense pulse

            if hit:
                if stable_since is None:
                    stable_since = now
                elif time.ticks_diff(now, stable_since) >= config.KABEL_CONNECT_STABLE_MS:
                    self.progress += 1
                    stable_since = None
                    blink_on = True
                    last_blink = now
                    if self.progress >= self.n:
                        self._win_animation()
                        return True
            else:
                stable_since = None

            if time.ticks_diff(now, start) >= config.KABEL_GAME_DURATION_MS:
                self._all_off()
                return False
