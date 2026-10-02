import time

class Countdown:
    def __init__(self, duration):
        self.duration = duration
        self.remaining_time = duration
        self.running = False

    def start(self):
        self.running = True
        self.remaining_time = self.duration
        while self.remaining_time > 0 and self.running:
            time.sleep(1)
            self.remaining_time -= 1

    def stop(self):
        self.running = False

    def get_remaining_time(self):
        return self.remaining_time

    def is_running(self):
        return self.running