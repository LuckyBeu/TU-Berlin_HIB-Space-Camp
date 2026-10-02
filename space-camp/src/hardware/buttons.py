from gpiozero import Button


class ButtonHandler:
    def __init__(self, button_pins, bounce_time=0.1):
        # button_pins: list of BCM pin numbers
        # bounce_time: hardware debounce handled by gpiozero
        self.buttons = [Button(pin, bounce_time=bounce_time) for pin in button_pins]

    def get_pressed_buttons(self):
        """Return list of indices of currently pressed buttons."""
        return [i for i, button in enumerate(self.buttons) if button.is_pressed]

    def wait_for_button_press(self):
        """Block until a button is pressed, return its index."""
        while True:
            pressed = self.get_pressed_buttons()
            if pressed:
                return pressed[0]