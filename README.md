# HIB Space Camp

An interactive, multi-device space-themed game system built for the **TU Berlin HIB Space Camp**. Players complete a sequence of mini-games using a wearable glove and physical stations, coordinated by a Raspberry Pi and two Raspberry Pi Pico 2 W microcontrollers over a local WiFi network.

## Overview

The game guides players through a space mission with three exercises. A Raspberry Pi acts as the central game master: it plays audio, reads the glove input, and starts mini-games on the Pico slaves over UDP. Each Pico runs one mini-game locally and reports the result (win/lose) back to the Pi.

```
                 ┌─────────────────────────┐
                 │      Raspberry Pi       │
                 │   (space-camp, master)  │
                 │  - Game loop & audio    │
                 │  - Glove (buttons/LEDs) │
                 │  - WiFi Access Point    │
                 └───────────┬─────────────┘
                             │ UDP (port 5005)
              ┌──────────────┴───────────────┐
              │                              │
   ┌──────────▼──────────┐       ┌───────────▼─────────────┐
   │   Pico 2 W (slave)  │       │     Pico 2 W (slave)    │
   │     kabelsalat      │       │   countdown_rocket-game │
   │  Cable-wiring game  │       │   Docking + countdown   │
   └─────────────────────┘       └─────────────────────────┘
```

## Game Flow

The mission consists of three exercises, played in sequence:

| Exercise | Name | Runs on | Description |
|----------|------|---------|-------------|
| 1 | **Finger Yoga** | Raspberry Pi (glove) | Press glove buttons in a random 10-step sequence (no finger twice in a row). |
| 2 | **Kabelsalat** | Kabelsalat Pico | Connect cables in the correct order. |
| 3 | **Docking** | Rocket Pico | Fly a rocket through space, avoid obstacles, and dock at the station. |

Completing all three → **success** (congrats audio). Failing any → **game over**.

## Subprojects

### 🧤 `space-camp` — Raspberry Pi game master

The central controller running on a Raspberry Pi (e.g. Model 3B+). It:

- Runs the main game loop and station sequence.
- Reads the **glove** (fingertip buttons) and controls the glove LEDs.
- Plays audio tracks via `aplay`.
- Hosts the WiFi **Access Point** the Picos connect to.
- Starts Pico mini-games over UDP and waits for their results.

**Key files:**
- `src/main.py` — entry point.
- `src/game/game_loop.py` — mission flow (intro → exercises → congrats/game over).
- `src/game/stations.py` — station/exercise definitions.
- `src/hardware/glove.py` — glove button/LED GPIO handling.
- `src/audio/audio_player.py` — audio playback and background loop.
- `src/network/countdown_server.py` — UDP server to start mini-games and receive results.
- `src/config/settings.py` — pins, network (UDP port, broadcast address), audio paths.

**Run:**
```bash
cd space-camp/src
python3 main.py
```

> Note: Large audio assets (e.g. `background.wav`) are not stored in Git and must be copied to `space-camp/assets/audio/` on the Pi separately.

### 🔌 `kabelsalat` — Cable-wiring mini-game (Pico 2 W)

A MicroPython slave running on a Raspberry Pi Pico 2 W. The player must connect cables in the correct order within a time limit. The Pico:

- Connects to the Pi's Access Point on boot.
- Waits for a UDP command `{"cmd":"game","mode":"kabelsalat"}`.
- Runs the wiring round and reports `{"cmd":"result","win":bool}` back to the Pi.

**Key files:**
- `main.py` — WiFi connect + UDP game router.
- `game.py` — wiring game logic (`run()` → returns win/lose).
- `netsync.py` — UDP listener/sender.
- `config.py` — LED/button GPIO pins, network settings, timing.
- `test_local.py` — local test without the Pi/network.

**Deploy (example):**
```bash
mpremote connect COM_PORT fs cp *.py :
mpremote connect COM_PORT run main.py
```

### 🚀 `countdown_rocket-game` — Docking game + countdown (Pico 2 W)

A MicroPython slave on a second Pico 2 W driving a 32×8 WS2812 LED matrix. It shows a shared countdown and runs the **Docking** mini-game.

- **Countdown:** displays a synchronized countdown driven by the Pi.
- **Docking (`docking.py`):** two phases —
  1. *Flight*: the rocket dodges obstacles while the world scrolls.
  2. *Docking*: the rocket approaches and must align with the station's target row to dock.
- Reports win/lose back to the Pi over UDP, same protocol as Kabelsalat.

**Key files:**
- `main.py` — WiFi connect + UDP router (`run_game` dispatches to the docking game).
- `docking.py` — `DockingGame` with `run()` → returns `True` (docked) / `False` (crash/timeout).
- `countdown.py` — countdown logic.
- `display.py` — WS2812 matrix driver (serpentine 32×8).
- `scroller.py` — non-blocking text scroller.
- `netsync.py` — UDP listener/sender.
- `config.py` — LED matrix, gameplay timing, network settings.

## Network Protocol

All devices communicate over UDP on port **5005** on the `192.168.4.x` network (the Pi's AP).

| Message | Direction | Payload |
|---------|-----------|---------|
| Start game | Pi → Pico | `{"cmd":"game","mode":"docking"\|"kabelsalat"}` |
| Countdown | Pi → Pico | `{"cmd":"start"\|"sync","ms":<remaining>}` |
| Reset | Pi → Pico | `{"cmd":"reset"}` |
| Result | Pico → Pi | `{"cmd":"result","win":true\|false}` |

Both Picos listen on the same port; each only reacts to its own `mode`.

## Requirements

**Raspberry Pi (`space-camp`):**
- Raspberry Pi OS, Python 3
- Configured as a WiFi Access Point (`SpaceCamp`, `192.168.4.1`)
- Audio output + `aplay`
- Glove hardware (buttons + LEDs on GPIO)

**Pico 2 W (`kabelsalat`, `countdown_rocket-game`):**
- MicroPython firmware
- WS2812 LED matrix (rocket game) / LEDs + buttons (kabelsalat)
- `mpremote` for deployment

## Getting Started

1. Flash MicroPython onto both Picos and copy the respective project files.
2. Set up the Raspberry Pi as the `SpaceCamp` Access Point.
3. Copy the audio assets to `space-camp/assets/audio/`.
4. Power on both Picos (they auto-connect to the AP and wait for commands).
5. On the Pi:
   ```bash
   cd space-camp/src
   python3 main.py
   ```

## Repository Structure

```
TU-Berlin_HIB-Space-Camp/
├── space-camp/              # Raspberry Pi game master
│   ├── src/                 # Game loop, hardware, audio, network, config
│   ├── assets/audio/        # Audio tracks (large files kept out of Git)
│   └── tests/
├── kabelsalat/              # Pico: cable-wiring mini-game
└── countdown_rocket-game/   # Pico: countdown + docking mini-game
```

## License

This project is part of the TU Berlin HIB Space Camp project.