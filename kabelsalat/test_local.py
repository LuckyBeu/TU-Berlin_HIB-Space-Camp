"""Lokaler Test des Kabelsalat-Spiels ohne Raspberry Pi / WLAN.

Startet das Spiel direkt und wiederholt es nach jedem Durchlauf. Auf den Pico
spielen und starten mit:

    mpremote run test_local.py

oder dauerhaft als Autostart kopieren (ersetzt main.py-Verhalten nur zum Test):

    mpremote cp test_local.py :test_local.py
    mpremote run test_local.py
"""
import time

from game import Kabelsalat


def main():
    print("Kabelsalat - LOKALER TEST (ohne Pi)")
    game = Kabelsalat(listener=None)

    while True:
        print("[test] neues Spiel - obere Ziel-LED mit passender unterer verbinden")
        win = game.run()
        print("[test] Ergebnis:", "GEWONNEN" if win else "verloren/timeout")
        time.sleep(2)


if __name__ == "__main__":
    main()
