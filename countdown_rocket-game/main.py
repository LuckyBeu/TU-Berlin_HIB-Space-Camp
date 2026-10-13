"""Entry point for the Space Camp Pico 2 W slave.

Runs two modes, switched by UDP commands from the Raspberry Pi:
  - countdown  (default): shows the SS:cc countdown
  - docking    (minigame): runs the docking game, reports the result back
"""
import time
import config
from display import Display
from netsync import start_wifi, poll_wifi, UdpListener
from countdown import Countdown
from scroller import TextScroller
from docking import DockingGame


def connect_with_message(display):
    """Scroll 'No connection!' until WiFi is up, then show 'Connected!' once."""
    print("[connect] creating scroller")
    scroller = TextScroller(display, "NO CONNECTION!", config.RED,
                            speed_ms=60, loop=True)
    print("[connect] starting wifi")
    wlan = start_wifi()

    next_check = time.ticks_ms()
    while True:
        scroller.update()
        now = time.ticks_ms()
        if time.ticks_diff(now, next_check) >= 0:
            next_check = time.ticks_add(now, 500)
            if poll_wifi(wlan):
                break
        time.sleep_ms(2)

    print("[connect] WiFi connected:", wlan.ifconfig())
    connected = TextScroller(display, "CONNECTED!", config.GREEN,
                             speed_ms=55, loop=False)
    while not connected.update():
        time.sleep_ms(2)

    display.clear()
    display.write()
    return wlan


def run_countdown(display, listener, countdown):
    """Countdown mode. Returns a pending 'game' command if one arrives."""
    frame_ms = 1000 // config.DISPLAY_FPS
    next_frame = time.ticks_ms()

    while True:
        cmd = listener.poll()
        if cmd:
            if cmd.get("cmd") == "game":
                return cmd  # hand control to the game router
            print("[main] cmd received:", cmd)
            countdown.handle(cmd)

        now = time.ticks_ms()
        if time.ticks_diff(now, next_frame) >= 0:
            countdown.update()
            next_frame = time.ticks_add(now, frame_ms)

        time.sleep_ms(2)


def run_game(display, listener, mode):
    """Dispatch to the requested minigame and report the result."""
    print("[main] starting game:", mode)
    if mode == "docking":
        game = DockingGame(display, listener=listener)
        win = game.run()
        print("[main] docking result:", win)
        listener.send_result(win)
    else:
        print("[main] unknown game mode:", mode)

    # clear the display before returning to countdown mode
    display.clear()
    display.write()


def main():
    print("Space Camp Pico - starting")
    display = Display()

    # Quick self-test
    display.clear()
    for x in range(3):
        display.set_pixel(x, 0, config.WHITE)
    display.write()
    time.sleep(1)
    display.clear()
    display.write()

    connect_with_message(display)

    listener = UdpListener()
    countdown = Countdown(display)
    print("[main] entering main router loop")

    while True:
        # Countdown mode runs until a game command arrives
        pending = run_countdown(display, listener, countdown)
        if pending and pending.get("cmd") == "game":
            run_game(display, listener, pending.get("mode"))
            # after the game, return to idle countdown
            countdown.handle({"cmd": "reset"})


if __name__ == "__main__":
    main()