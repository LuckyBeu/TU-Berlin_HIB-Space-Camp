"""Docking minigame for the Pico 2 W (station 2).

Two phases:
  1. Flight  (0..55s): rocket fixed on the right (cols 29-31), world scrolls
                       left, obstacles fly in from the right edge and pass by.
                       Gravity pulls down; UP lifts, DOWN drops faster.
  2. Docking (>=55s):  no new obstacles, existing ones scroll out, a green
                       station appears on the right, the rocket drives toward
                       it. Must be on the target row (row 5) to dock.

Runs fully local on the Pico (no network in the loop).
Use run() -> returns True (docked) or False (crash/timeout).
"""
import time
import random
from machine import Pin

import config


class Obstacle:
    def __init__(self, x, row, size):
        self.x = x          # left column (may be fractional via sub-steps)
        self.row = row      # top row
        self.size = size    # 1 (single pixel) or 2 (2x2 block)
        self.v_dir = 1 if random.getrandbits(1) else -1

    def cells(self):
        out = []
        for dx in range(self.size):
            for dy in range(self.size):
                out.append((self.x + dx, self.row + dy))
        return out


class DockingGame:
    def __init__(self, display, listener=None):
        """display: your Display instance. listener: optional UdpListener
        so the game can keep draining packets (ignored during play)."""
        self.d = display
        self.listener = listener
        self.btn_up = Pin(config.DOCK_BTN_UP_PIN, Pin.IN, Pin.PULL_UP)
        self.btn_down = Pin(config.DOCK_BTN_DOWN_PIN, Pin.IN, Pin.PULL_UP)

        self.W = config.DOCK_FIELD_WIDTH
        self.H = config.DOCK_FIELD_HEIGHT
        self.rw = config.DOCK_ROCKET_WIDTH

    # -- lifecycle ----------------------------------------------------------
    def _reset(self):
        self.rocket_x = config.DOCK_ROCKET_X
        self.rocket_row = config.DOCK_START_ROW
        self.obstacles = []
        self.phase = 1
        self.start_ms = time.ticks_ms()

        self._last_frame = 0
        self._last_scroll = 0
        self._last_gravity = 0
        self._last_spawn = 0
        self._last_obs_v = 0
        self._last_approach = 0

        self._up_prev = 1
        self._down_prev = 1

    # -- input --------------------------------------------------------------
    def _read_buttons(self):
        up = self.btn_up.value()
        down = self.btn_down.value()
        up_edge = (up == 0 and self._up_prev == 1)
        down_edge = (down == 0 and self._down_prev == 1)
        self._up_prev = up
        self._down_prev = down
        return up_edge, down_edge

    # -- physics ------------------------------------------------------------
    def _apply_gravity(self, now):
        if not config.DOCK_GRAVITY_ENABLED:
            return
        if time.ticks_diff(now, self._last_gravity) >= config.DOCK_GRAVITY_INTERVAL_MS:
            self._last_gravity = now
            self.rocket_row = min(self.H - 1, self.rocket_row + 1)

    def _apply_input(self, up_edge, down_edge):
        if up_edge:
            self.rocket_row = max(0, self.rocket_row - 1)
        if down_edge:
            self.rocket_row = min(self.H - 1, self.rocket_row + 1)

    def _scroll_world(self, now):
        if time.ticks_diff(now, self._last_scroll) >= config.DOCK_SCROLL_INTERVAL_MS:
            self._last_scroll = now
            for o in self.obstacles:
                o.x -= 1
            self.obstacles = [o for o in self.obstacles if o.x + o.size > 0]

    def _move_obstacles_v(self, now):
        if time.ticks_diff(now, self._last_obs_v) >= config.DOCK_OBSTACLE_V_INTERVAL_MS:
            self._last_obs_v = now
            for o in self.obstacles:
                o.row += o.v_dir
                if o.row <= 0:
                    o.row = 0
                    o.v_dir = 1
                elif o.row + o.size >= self.H:
                    o.row = self.H - o.size
                    o.v_dir = -1

    def _spawn_obstacle(self, now):
        """Spawn obstacles that FLY IN from the right edge."""
        if time.ticks_diff(now, self._last_spawn) >= config.DOCK_OBSTACLE_SPAWN_MS:
            self._last_spawn = now
            size = 2 if random.getrandbits(1) else 1
            row = random.randint(0, self.H - size)
            # enter from the right edge of the field, then scroll left
            self.obstacles.append(Obstacle(self.W - 1, row, size))

    # -- collision ----------------------------------------------------------
    def _rocket_cells(self):
        return [(self.rocket_x + i, self.rocket_row) for i in range(self.rw)]

    def _check_collision(self):
        rocket = set(self._rocket_cells())
        for o in self.obstacles:
            for cell in o.cells():
                if cell in rocket:
                    return True
        return False

    # -- rendering ----------------------------------------------------------
    def _px(self, x, y, color):
        """Set a pixel, flipping Y so row 0 is the TOP of the display."""
        self.d.set_pixel(x, (self.H - 1) - y, color)

    def _draw(self, station_x=None):
        self.d.clear()
        # obstacles
        for o in self.obstacles:
            for (x, y) in o.cells():
                if 0 <= x < self.W and 0 <= y < self.H:
                    self.d.set_pixel(x, y, config.DOCK_COLOR_OBSTACLE)
        # docking station (phase 2)
        if station_x is not None:
            half = config.DOCK_ZONE_HEIGHT // 2
            for dy in range(config.DOCK_ZONE_HEIGHT):
                y = config.DOCK_TARGET_ROW - half + dy
                if 0 <= y < self.H:
                    self.d.set_pixel(station_x, y, config.DOCK_COLOR_STATION)
            if 0 <= config.DOCK_TARGET_ROW < self.H:
                self.d.set_pixel(station_x, config.DOCK_TARGET_ROW,
                                 config.DOCK_COLOR_TARGET)
        # rocket on top
        for (x, y) in self._rocket_cells():
            if 0 <= x < self.W and 0 <= y < self.H:
                self.d.set_pixel(x, y, config.DOCK_COLOR_ROCKET)
        self.d.write()

    def _flash(self, color, times=3):
        """Brief full-screen flash for win/lose feedback."""
        for _ in range(times):
            self.d.clear()
            for x in range(self.W):
                for y in range(self.H):
                    self.d.set_pixel(x, y, color)
            self.d.write()
            time.sleep_ms(120)
            self.d.clear()
            self.d.write()
            time.sleep_ms(120)

    # -- main loop ----------------------------------------------------------
    def run(self):
        """Run the game. Returns True on successful docking, else False."""
        self._reset()

        while True:
            now = time.ticks_ms()
            elapsed = time.ticks_diff(now, self.start_ms)

            # keep draining network packets so the socket doesn't back up
            if self.listener:
                self.listener.poll()

            # frame pacing
            if time.ticks_diff(now, self._last_frame) < config.DOCK_FRAME_INTERVAL_MS:
                time.sleep_ms(2)
                continue
            self._last_frame = now

            up_edge, down_edge = self._read_buttons()

            # phase transition
            if self.phase == 1 and elapsed >= config.DOCK_STATION_APPEAR_MS:
                self.phase = 2
                self._last_approach = now

            if self.phase == 1:
                self._spawn_obstacle(now)
                self._scroll_world(now)
                self._move_obstacles_v(now)
                self._apply_input(up_edge, down_edge)
                self._apply_gravity(now)

                if self._check_collision():
                    self._flash(config.DOCK_COLOR_OBSTACLE)
                    return False
                self._draw()

            else:  # phase 2: docking
                self._scroll_world(now)
                self._move_obstacles_v(now)
                self._apply_input(up_edge, down_edge)
                self._apply_gravity(now)

                if time.ticks_diff(now, self._last_approach) >= config.DOCK_APPROACH_INTERVAL_MS:
                    self._last_approach = now
                    if self.rocket_x + self.rw - 1 < config.DOCK_STATION_X:
                        self.rocket_x += 1

                if self._check_collision():
                    self._flash(config.DOCK_COLOR_OBSTACLE)
                    return False

                self._draw(station_x=config.DOCK_STATION_X)

                # docking check: rocket tip reached the station column
                if self.rocket_x + self.rw - 1 >= config.DOCK_STATION_X:
                    win = (self.rocket_row == config.DOCK_TARGET_ROW)
                    self._flash(config.DOCK_COLOR_TARGET if win
                                else config.DOCK_COLOR_OBSTACLE)
                    return win

            if elapsed >= config.DOCK_GAME_DURATION_MS:
                return False