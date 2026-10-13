"""Entry point for the Kabelsalat Pico 2 W slave.

Connects to the Raspberry Pi access point (same AP as the countdown/docking
Pico), then waits for a UDP game command and runs the wiring minigame,
reporting the win/lose result back over UDP.
"""
import time

from machine import Pin

import config
from netsync import start_wifi, poll_wifi, UdpListener
from game import Kabelsalat


def _upper_pins():
    """Create the upper-row LED pins as high-Z inputs (all off)."""
    return [Pin(p, Pin.IN) for p in (
        config.LED_1_1, config.LED_1_2, config.LED_1_3,
        config.LED_1_4, config.LED_1_5)][:config.KABEL_LED_COUNT]


def connect_with_feedback():
    """Sweep the upper LEDs (knight-rider) until WiFi is up, then blank them."""
    pins = _upper_pins()
    n = len(pins)

    def light(idx):
        """Light only the upper LED at idx, release the rest."""
        for i, p in enumerate(pins):
            if i == idx:
                p.init(Pin.OUT)
                p.value(0)
            else:
                p.init(Pin.IN)

    print("[kabelsalat] connecting to WiFi")
    wlan = start_wifi()

    pos, step = 0, 1
    next_step = time.ticks_ms()
    next_check = time.ticks_ms()
    while True:
        now = time.ticks_ms()
        if time.ticks_diff(now, next_step) >= 0:
            next_step = time.ticks_add(now, 90)
            light(pos)
            pos += step
            if pos >= n - 1:
                pos, step = n - 1, -1
            elif pos <= 0:
                pos, step = 0, 1
        if time.ticks_diff(now, next_check) >= 0:
            next_check = time.ticks_add(now, 500)
            if poll_wifi(wlan):
                break
        time.sleep_ms(5)

    for p in pins:
        p.init(Pin.IN)
    print("[kabelsalat] WiFi connected:", wlan.ifconfig())
    return wlan


def main():
    """Connect to WiFi, then run the wiring game on each 'game' command."""
    print("Kabelsalat Pico - starting")
    connect_with_feedback()

    listener = UdpListener()
    game = Kabelsalat(listener=listener)
    print("[kabelsalat] entering router loop")

    while True:
        cmd = listener.poll()
        if cmd and cmd.get("cmd") == "game" and cmd.get("mode") == config.KABEL_GAME_MODE:
            print("[kabelsalat] starting game")
            win = game.run()
            print("[kabelsalat] result:", win)
            listener.send_result(win)
        time.sleep_ms(20)


if __name__ == "__main__":
    main()
