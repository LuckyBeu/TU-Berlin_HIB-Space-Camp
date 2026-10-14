from config import settings
from hardware.glove import Glove
from audio.audio_player import AudioPlayer
from game.game_loop import GameLoop
from game.stations import create_stations
from network.countdown_server import CountdownServer


def main():
    glove = Glove(settings.BUTTON_PINS, settings.LED_PINS)
    audio = AudioPlayer(settings.AUDIO_TRACKS)
    countdown_server = CountdownServer()

    game = GameLoop(
        glove,
        audio,
        countdown_time=settings.COUNTDOWN_TIME,
        debounce_time=settings.BUTTON_DEBOUNCE_TIME,
        countdown_server=countdown_server,
        stations=create_stations(list(settings.BUTTON_PINS.keys())),
    )
    game.run()


if __name__ == "__main__":
    main()