import unittest
from src.game.game_loop import GameLoop

class TestGameLoop(unittest.TestCase):

    def setUp(self):
        self.game_loop = GameLoop()

    def test_initialization(self):
        self.assertIsNotNone(self.game_loop)

    def test_start_game(self):
        self.game_loop.start_game()
        self.assertTrue(self.game_loop.is_running)

    def test_play_audio_on_action(self):
        self.game_loop.play_audio_on_action('button_press')
        self.assertIn('button_press_audio', self.game_loop.played_audio)

    def test_check_user_input(self):
        self.game_loop.check_user_input('valid_input')
        self.assertTrue(self.game_loop.is_input_valid)

    def test_end_game(self):
        self.game_loop.end_game()
        self.assertFalse(self.game_loop.is_running)

if __name__ == '__main__':
    unittest.main()