"""Entry point for the Space Camp countdown slave (Pico 2 W)."""
import time
import config
from display import Display
from netsync import start_wifi, poll_wifi, UdpListener
from countdown import Countdown
from scroller import TextScroller


def connect_with_message(display):
    """Scroll 'No connection!' until WiFi is up, then show 'Connected!' once."""
    print("[connect] creating scroller")
    scroller = TextScroller(display, "NO CONNECTION!", config.RED,
                            speed_ms=60, loop=True)
    print("[connect] scroller width =", display.text_width("NO CONNECTION!"))

    print("[connect] starting wifi")
    wlan = start_wifi()
    print("[connect] wifi started, entering loop")

    next_check = time.ticks_ms()
    frames = 0
    while True:
        scroller.update()
        frames += 1

        now = time.ticks_ms()
        if time.ticks_diff(now, next_check) >= 0:
            next_check = time.ticks_add(now, 500)
            status = wlan.status()
            print("[connect] frames={} wifi.status={} connected={}".format(
                frames, status, wlan.isconnected()))
            if poll_wifi(wlan):
                break

        time.sleep_ms(2)

    print("[connect] WiFi connected:", wlan.ifconfig())

    connected = TextScroller(display, "CONNECTED!", config.GREEN,
                             speed_ms=55, loop=False)
    while not connected.update():
        time.sleep_ms(2)
    print("[connect] 'Connected!' scroll done")

    display.clear()
    display.write()
    return wlan


def main():
    print("Space Camp Countdown - starting")

    print("[main] initializing display")
    display = Display()
    print("[main] display ready: {}x{}".format(display.width, display.height))

    # Quick self-test: light the first few pixels white for ~1 s
    display.clear()
    for x in range(3):
        display.set_pixel(x, 0, config.WHITE)
    display.write()
    print("[main] self-test pixels written (expect 3 white dots top-left)")
    time.sleep(1)

    display.clear()
    display.write()

    connect_with_message(display)

    print("[main] starting listener")
    listener = UdpListener()
    countdown = Countdown(display)

    frame_ms = 1000 // config.DISPLAY_FPS
    next_frame = time.ticks_ms()
    print("[main] entering countdown loop")

    while True:
        cmd = listener.poll()
        if cmd:
            print("[main] cmd received:", cmd)
            countdown.handle(cmd)

        now = time.ticks_ms()
        if time.ticks_diff(now, next_frame) >= 0:
            countdown.update()
            next_frame = time.ticks_add(now, frame_ms)

        time.sleep_ms(2)


if __name__ == "__main__":
    main()