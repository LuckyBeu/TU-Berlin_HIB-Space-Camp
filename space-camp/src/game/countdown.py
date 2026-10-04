"""Game-level countdown.

Thin, non-blocking wrapper around the network CountdownServer. The server
holds the authoritative time and broadcasts it to the Pico displays.
"""
from network.countdown_server import CountdownServer


class Countdown:
    def __init__(self, duration, server=None):
        self.duration = duration
        self.server = server or CountdownServer()

    def start(self):
        """Start the countdown (non-blocking). Picos update automatically."""
        self.server.start(self.duration)

    def stop(self):
        self.server.reset()

    def pause(self):
        self.server.pause()

    def resume(self):
        self.server.resume()

    def get_remaining_time(self):
        """Remaining time in whole seconds."""
        return self.server.get_remaining_ms() // 1000

    def is_running(self):
        return self.server.is_running()