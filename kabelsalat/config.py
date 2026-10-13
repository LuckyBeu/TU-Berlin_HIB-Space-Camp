# ===== HARDWARE CONFIGURATION =====
LED_1_1 = 0               # GPIO for LED 1.1
LED_1_2 = 1               # GPIO for LED 1.2
LED_1_3 = 2               # GPIO for LED 1.3
LED_1_4 = 3               # GPIO for LED 1.4
LED_1_5 = 4               # GPIO for LED 1.5

LED_2_1 = 5               # GPIO for LED 2.1
LED_2_2 = 6               # GPIO for LED 2.2
LED_2_3 = 7               # GPIO for LED 2.3
LED_2_4 = 8               # GPIO for LED 2.4
LED_2_5 = 9               # GPIO for LED 2.5


# ===== NETWORK CONFIGURATION =====
WIFI_SSID = "SpaceCamp"       # Access Point SSID (Raspberry Pi 3)
WIFI_PASSWORD = "spacecamp123"
UDP_PORT = 5005               # Port for countdown broadcasts
WIFI_CONNECT_TIMEOUT = 15     # seconds


# ===== KABELSALAT GAME =====
KABEL_LED_COUNT = 5               # LEDs per row (must match the pin lists above)
KABEL_GAME_MODE = "kabelsalat"    # UDP "game" mode that starts this minigame
KABEL_FRAME_MS = 20               # main loop frame interval
KABEL_BLINK_MS = 350              # on/off half-period of the current target LED
KABEL_SENSE_SETTLE_US = 120       # settle time before reading a sensed pin
KABEL_CONNECT_STABLE_MS = 150     # a connection must hold this long to count
KABEL_GAME_DURATION_MS = 120000   # safety timeout -> game lost