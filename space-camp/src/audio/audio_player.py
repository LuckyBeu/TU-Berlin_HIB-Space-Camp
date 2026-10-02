import subprocess
import os


class AudioPlayer:
    def __init__(self, tracks):
        # tracks: dict mapping name -> file path
        self.tracks = tracks

    def play(self, name, blocking=True):
        path = self.tracks.get(name)
        if path is None:
            raise ValueError(f"Unknown audio track: {name}")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Audio file not found: {path}")

        # aplay handles .wav files and is available on Raspberry Pi OS
        if blocking:
            subprocess.run(["aplay", "-q", path])
        else:
            return subprocess.Popen(["aplay", "-q", path])