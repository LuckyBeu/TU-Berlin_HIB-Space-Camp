import unittest
from src.hardware.glove import Glove

class TestGlove(unittest.TestCase):
    def setUp(self):
        self.glove = Glove()

    def test_button_press(self):
        # Simulate a button press and check the response
        self.glove.press_button(0)  # Assuming button 0 is pressed
        self.assertTrue(self.glove.is_button_pressed(0))

    def test_button_release(self):
        # Simulate a button release and check the response
        self.glove.release_button(0)  # Assuming button 0 is released
        self.assertFalse(self.glove.is_button_pressed(0))

    def test_multiple_button_presses(self):
        # Simulate multiple button presses and check the responses
        buttons_to_press = [0, 1, 2]
        for button in buttons_to_press:
            self.glove.press_button(button)
            self.assertTrue(self.glove.is_button_pressed(button))

    def test_force_feedback(self):
        # Test the force feedback functionality
        self.glove.trigger_force_feedback(1)  # Assuming 1 is a valid feedback level
        self.assertTrue(self.glove.is_feedback_triggered())

if __name__ == '__main__':
    unittest.main()