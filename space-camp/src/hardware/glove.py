import RPi.GPIO as GPIO

class Glove:
    def __init__(self, button_pins):
        # button_pins: dict like {"index": 17, "middle": 27, "pinky": 22}
        self.button_pins = button_pins
        GPIO.setmode(GPIO.BCM)
        for pin in self.button_pins.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read_buttons(self):
        # Returns dict like {"index": True, "middle": False, ...}
        return {
            name: GPIO.input(pin) == GPIO.LOW
            for name, pin in self.button_pins.items()
        }

    def cleanup(self):
        GPIO.cleanup()