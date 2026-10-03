"""Standalone NeoPixel driver for the countdown display (32x8 serpentine matrix)."""
from machine import Pin
from neopixel import NeoPixel
import config


class Display:
    """Wraps a serpentine-wired 32x8 NeoPixel matrix with brightness control."""

    def __init__(self, pin=config.LED_PIN, count=config.LED_COUNT,
                 brightness=config.DEFAULT_BRIGHTNESS):
        self.np = NeoPixel(Pin(pin), count)
        self.width = config.DISPLAY_WIDTH
        self.height = config.DISPLAY_HEIGHT
        self.set_brightness(brightness)

    def set_brightness(self, brightness):
        self._brightness = min(max(brightness, 0.0), 1.0)

    def _scale(self, color):
        if self._brightness >= 0.999:
            return color
        b = self._brightness
        return (int(color[0] * b), int(color[1] * b), int(color[2] * b))

    def xy_to_index(self, x, y):
        """Convert (x, y) to strip index using serpentine wiring."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError("Coordinates out of bounds: ({}, {})".format(x, y))
        if x % 2 == 1:
            return x * self.height + (self.height - 1 - y)
        return x * self.height + y

    def clear(self):
        self.np.fill((0, 0, 0))

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.np[self.xy_to_index(x, y)] = self._scale(color)

    def draw_digit(self, digit, start_x, start_y, color):
        """Draw a single digit (0-9) using the 5x7 font."""
        glyph = config.FONT_5X7[str(digit)]
        for row, bits in enumerate(glyph):
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.set_pixel(start_x + col, start_y + row, color)

    def draw_char(self, ch, start_x, start_y, color):
        """Draw a single font character at (start_x, start_y)."""
        glyph = config.FONT_5X7.get(ch.upper())
        if glyph is None:
            return
        for row, bits in enumerate(glyph):
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.set_pixel(start_x + col, start_y + row, color)

    def draw_text(self, text, start_x, start_y, color, spacing=1):
        """Draw a string starting at start_x. Characters are 5px wide."""
        x = start_x
        for ch in text:
            self.draw_char(ch, x, start_y, color)
            x += 5 + spacing

    @staticmethod
    def text_width(text, spacing=1):
        """Pixel width of a rendered string."""
        if not text:
            return 0
        return len(text) * (5 + spacing) - spacing

    def write(self):
        self.np.write()