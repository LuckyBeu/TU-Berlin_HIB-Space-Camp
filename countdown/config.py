# ===== HARDWARE CONFIGURATION =====
LED_PIN = 0               # GPIO data line for WS2812
LED_COUNT = 256           # 8x32 = 256 LEDs
DISPLAY_WIDTH = 32
DISPLAY_HEIGHT = 8
DEFAULT_BRIGHTNESS = 0.1  # 0.0 to 1.0

# ===== NETWORK CONFIGURATION =====
WIFI_SSID = "SpaceCamp"       # Access Point SSID (Raspberry Pi 3)
WIFI_PASSWORD = "spacecamp123"
UDP_PORT = 5005               # Port for countdown broadcasts
WIFI_CONNECT_TIMEOUT = 15     # seconds

# ===== COLOR DEFINITIONS (R, G, B) =====
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 80, 0)

# ===== COUNTDOWN DISPLAY COLORS =====
NORMAL_COLOR = CYAN       # color while counting down
WARNING_COLOR = ORANGE    # color when < WARNING_THRESHOLD_S
CRITICAL_COLOR = RED      # color when < CRITICAL_THRESHOLD_S
FINISHED_COLOR = RED      # color when time is up (blinks)
SEPARATOR_COLOR = WHITE

WARNING_THRESHOLD_S = 10
CRITICAL_THRESHOLD_S = 5

# ===== COUNTDOWN STATES =====
STATE_IDLE = 0        # waiting for a command
STATE_RUNNING = 1     # counting down
STATE_PAUSED = 2      # paused
STATE_FINISHED = 3    # reached zero

# ===== FONT DEFINITION (5x7) =====
FONT_5X7 = {
    '0': [0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110],
    '1': [0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    '2': [0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111],
    '3': [0b01110, 0b10001, 0b00001, 0b00110, 0b00001, 0b10001, 0b01110],
    '4': [0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010],
    '5': [0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110],
    '6': [0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110],
    '7': [0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10000],
    '8': [0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110],
    '9': [0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100],
    # Letters (uppercase)
    'A': [0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001],
    'C': [0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110],
    'D': [0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110],
    'E': [0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111],
    'I': [0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110],
    'N': [0b10001, 0b11001, 0b11001, 0b10101, 0b10011, 0b10011, 0b10001],
    'O': [0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110],
    'T': [0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100],
    # Punctuation / space
    ' ': [0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000],
    '!': [0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100],
}

# ===== DISPLAY UPDATE =====
DISPLAY_FPS = 30          # frames per second for rendering

# ---------------------------------------------------------------------------
# Docking minigame (station 2)
# ---------------------------------------------------------------------------
DOCK_FIELD_WIDTH = 32
DOCK_FIELD_HEIGHT = 8
DOCK_ROCKET_WIDTH = 3

# Phase 1: flight (rocket fixed on the LEFT, world scrolls left)
DOCK_ROCKET_X = 1                 # rocket occupies columns 1,2,3
DOCK_START_ROW = 3                # start mid-field (room to maneuver up/down)
DOCK_SCROLL_INTERVAL_MS = 200     # world scrolls 1px every 0.2s (5 px/s)
DOCK_GRAVITY_ENABLED = False      # gravity off for now (manual up/down only)
DOCK_GRAVITY_INTERVAL_MS = 1000   # gentler: 1 row down every 1.0s
DOCK_OBSTACLE_SPAWN_MS = 2000     # new obstacle every 3.0s (half as many)
DOCK_OBSTACLE_V_INTERVAL_MS = 400 # obstacle moves 1 row vertically every 0.4s

# Phase 2: docking (station fixed right, rocket drives toward it)
DOCK_STATION_APPEAR_MS = 55000     # TEMP: station appears at 8s for quick testing
DOCK_APPROACH_INTERVAL_MS = 300   # rocket moves 1px right every 0.3s
DOCK_STATION_X = 31               # station column (rightmost)
DOCK_TARGET_ROW = 5               # fixed docking target row
DOCK_ZONE_HEIGHT = 2              # green zone height (target highlighted)

# General
DOCK_FRAME_INTERVAL_MS = 66       # ~15 FPS
DOCK_GAME_DURATION_MS = 60000     # 60s safety timeout

# Buttons (local to the Pico)
DOCK_BTN_UP_PIN = 7
DOCK_BTN_DOWN_PIN = 8
DOCK_BTN_DEBOUNCE_MS = 20

# Docking colors (reuse existing color constants)
DOCK_COLOR_ROCKET = WHITE
DOCK_COLOR_OBSTACLE = MAGENTA
DOCK_COLOR_STATION = GREEN
DOCK_COLOR_TARGET = GREEN