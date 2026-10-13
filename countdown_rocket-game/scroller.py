"""Non-blocking horizontal text scroller for the 32x8 matrix."""
import time
import config


class TextScroller:
    """Scrolls a text string from right to left.

    Call update() repeatedly. It returns True once the text has fully
    scrolled off the left edge (one complete pass).
    """

    def __init__(self, display, text, color, speed_ms=60, y=0, loop=True):
        self.display = display
        self.text = text
        self.color = color
        self.speed_ms = speed_ms
        self.y = y
        self.loop = loop
        self._width = display.text_width(text)
        self._x = display.width            # start off the right edge
        self._last = time.ticks_ms()

    def reset(self):
        self._x = self.display.width
        self._last = time.ticks_ms()

    def update(self):
        """Advance and render one frame. Returns True after a full pass."""
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last) >= self.speed_ms:
            self._x -= 1
            self._last = now
            # fully scrolled off the left edge
            if self._x < -self._width:
                if self.loop:
                    self._x = self.display.width
                else:
                    return True

        self.display.clear()
        self.display.draw_text(self.text, self._x, self.y, self.color)
        self.display.write()
        return False