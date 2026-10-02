from config import settings
from hardware.glove import Glove
from audio.audio_player import AudioPlayer
from game.game_loop import GameLoop


def main():
    glove = Glove(settings.BUTTON_PINS)
    audio = AudioPlayer(settings.AUDIO_TRACKS)
    game = GameLoop(
        glove=glove,
        audio_player=audio,
        countdown_time=settings.COUNTDOWN_TIME,
        debounce_time=settings.BUTTON_DEBOUNCE_TIME,
    )
    game.run()


if __name__ == "__main__":
    main()