import RPi.GPIO as GPIO

class Glove:
    def __init__(self, button_pins, led_pins):
        # button_pins: dict like {"index": 17, "middle": 27, "pinky": 22}
        self.button_pins = button_pins
        self.led_pins = led_pins
        GPIO.setmode(GPIO.BCM)
        # config button GPIOs
        for pin in self.button_pins.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # config LED GPIOs
        for pin in self.led_pins.values():
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    def read_buttons(self):
        # Returns dict like {"index": True, "middle": False, ...}
        return {
            name: GPIO.input(pin) == GPIO.LOW
            for name, pin in self.button_pins.items()
        }

    def set_led(self, name, on):
        GPIO.output(self.led_pins[name], GPIO.HIGH if on else GPIO.LOW)

    def set_leds(self, names, on=True):
        for name in names:
            self.set_led(name, on)

    def all_leds_off(self):
        for name in self.led_pins:
            self.set_led(name, False)

    def cleanup(self):
        GPIO.cleanup()