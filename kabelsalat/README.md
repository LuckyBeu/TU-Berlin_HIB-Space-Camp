# Kabelsalat

Ein interaktives Spiel für den Raspberry Pi, entwickelt im Rahmen des **TU-Berlin HIB Space Camp**.

## Überblick

Kabelsalat ist Teil des Space-Camp-Projekts und läuft auf einem Raspberry Pi.
Das Spiel nutzt eine Netzwerk-Synchronisation, um mehrere Geräte bzw. Stationen
koordiniert anzusteuern (z. B. für einen gemeinsamen Countdown oder Spielablauf).

## Projektstruktur

```
kabelsalat
├── config.py        # Konfiguration (Netzwerk, Pins, Timing, Pfade)
├── game.py          # Spiellogik und Spielablauf
├── main.py          # Einstiegspunkt zum Starten des Spiels
├── netsync.py       # Netzwerk-Synchronisation zwischen Geräten (UDP)
├── test_local.py    # Lokaler Test ohne Hardware/Netzwerk
└── README.md
```

## Voraussetzungen

- Raspberry Pi (z. B. Model 3B+) mit Raspberry Pi OS
- Python 3
- Verbundenes Netzwerk (z. B. Access Point) für die Synchronisation

## Installation

```bash
# Repository klonen
git clone git@github.com:LuckyBeu/TU-Berlin_HIB-Space-Camp.git
cd TU-Berlin_HIB-Space-Camp/kabelsalat

# Benötigte Pakete installieren (falls vorhanden)
pip3 install -r requirements.txt
```

## Konfiguration

Alle Einstellungen werden in [`config.py`](config.py ) vorgenommen, z. B.:

- Netzwerk-Parameter (UDP-Port, Broadcast-Adresse, Sync-Intervall)
- Timing-Einstellungen (z. B. Countdown-Dauer)
- Dateipfade (z. B. zu Audio-Assets)

Passe diese Werte vor dem Start an deine Umgebung an.

## Starten des Spiels

Auf dem Raspberry Pi:

```bash
python3 main.py
```

## Lokales Testen

Um die Spiellogik ohne angeschlossene Hardware oder Netzwerk zu testen:

```bash
python3 test_local.py
```

## Komponenten

| Datei | Beschreibung |
|-------|--------------|
| [`main.py`](main.py ) | Startet das Spiel und initialisiert die Komponenten. |
| [`game.py`](game.py ) | Enthält die Spiellogik und den Ablauf. |
| [`netsync.py`](netsync.py ) | Synchronisiert mehrere Geräte über das Netzwerk (UDP-Broadcast). |
| [`config.py`](config.py ) | Zentrale Konfiguration für Netzwerk, Timing und Pfade. |
| [`test_local.py`](test_local.py ) | Lokaler Testlauf ohne Hardwareabhängigkeiten. |

## Lizenz

Dieses Projekt ist Teil des TU-Berlin HIB Space Camp Projekts.