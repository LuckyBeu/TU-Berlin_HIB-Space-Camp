import unittest
from src.audio.audio_player import AudioPlayer

class TestAudioPlayer(unittest.TestCase):
    def setUp(self):
        self.audio_player = AudioPlayer()

    def test_load_audio(self):
        result = self.audio_player.load_audio('test_track.mp3')
        self.assertTrue(result)

    def test_play_audio(self):
        self.audio_player.load_audio('test_track.mp3')
        result = self.audio_player.play_audio()
        self.assertTrue(result)

    def test_stop_audio(self):
        self.audio_player.load_audio('test_track.mp3')
        self.audio_player.play_audio()
        result = self.audio_player.stop_audio()
        self.assertTrue(result)

    def test_audio_playback_state(self):
        self.audio_player.load_audio('test_track.mp3')
        self.audio_player.play_audio()
        self.assertTrue(self.audio_player.is_playing())
        self.audio_player.stop_audio()
        self.assertFalse(self.audio_player.is_playing())

if __name__ == '__main__':
    unittest.main()