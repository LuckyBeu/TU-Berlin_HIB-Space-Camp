import subprocess
import os
import threading


class AudioPlayer:
    def __init__(self, tracks):
        # tracks: dict mapping name -> file path
        self.tracks = tracks
        self._loop_stop = None
        self._loop_thread = None
        self._loop_proc = None

    def _resolve(self, name):
        path = self.tracks.get(name)
        if path is None:
            raise ValueError(f"Unknown audio track: {name}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Audio file not found: {path}")
        return path

    def play(self, name, blocking=True):
        path = self._resolve(name)

        # aplay handles .wav files and is available on Raspberry Pi OS
        if blocking:
            subprocess.run(["aplay", "-q", path])
        else:
            return subprocess.Popen(["aplay", "-q", path])

    def start_loop(self, name):
        """Play a track on repeat in the background until stop_loop() is called."""
        path = self._resolve(name)
        self.stop_loop()

        stop = threading.Event()

        def _loop():
            while not stop.is_set():
                self._loop_proc = subprocess.Popen(["aplay", "-q", path])
                self._loop_proc.wait()

        self._loop_stop = stop
        self._loop_thread = threading.Thread(target=_loop, daemon=True)
        self._loop_thread.start()

    def stop_loop(self):
        """Stop background loop playback started by start_loop()."""
        if self._loop_stop is not None:
            self._loop_stop.set()
        if self._loop_proc is not None and self._loop_proc.poll() is None:
            self._loop_proc.terminate()
        if self._loop_thread is not None:
            self._loop_thread.join(timeout=1)
        self._loop_stop = None
        self._loop_thread = None
        self._loop_proc = None