"""Countdown master for the Raspberry Pi 3 (access point).

Broadcasts countdown commands over UDP so all Pico 2 W slaves stay in sync.
Also sends periodic 'sync' packets with the authoritative remaining time to
correct clock drift on the slaves.

Usage (interactive):
    python3 countdown_server.py
    > start 60      # start a 60 second countdown
    > pause
    > resume
    > reset
    > quit
"""
import socket
import json
import threading
import time

from config.settings import UDP_PORT, AP_BIND_IP, BROADCAST_ADDR, SYNC_INTERVAL


class CountdownServer:
    def __init__(self, port=UDP_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to the AP interface so broadcasts leave via wlan0
        try:
            self.sock.bind((AP_BIND_IP, UDP_PORT))
            print("[server] bound to {} -> {}".format(AP_BIND_IP, self.sock.getsockname()))
        except OSError as e:
            print("Warning: could not bind to {}: {}".format(AP_BIND_IP, e))
        self.port = UDP_PORT

        self.remaining_ms = 0
        self.running = False
        self._ref = None
        self._lock = threading.Lock()

        self._stop = False
        self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._sync_thread.start()

    def _send(self, payload):
        data = json.dumps(payload).encode()
        print("[server] sending to {}:{} -> {}".format(BROADCAST_ADDR, self.port, payload))  # DEBUG
        self.sock.sendto(data, (BROADCAST_ADDR, self.port))

    def _tick_unlocked(self):
        """Update remaining_ms from the monotonic clock.

        Caller MUST already hold self._lock.
        """
        if self.running and self._ref is not None:
            now = time.monotonic()
            elapsed = int((now - self._ref) * 1000)
            self.remaining_ms = max(0, self.remaining_ms - elapsed)
            self._ref = now
            if self.remaining_ms == 0:
                self.running = False

    def tick(self):
        """Thread-safe refresh of remaining_ms. Safe to call from outside."""
        with self._lock:
            self._tick_unlocked()

    def start(self, seconds):
        with self._lock:
            self.remaining_ms = int(seconds * 1000)
            self.running = True
            self._ref = time.monotonic()
            self._send({"cmd": "start", "ms": self.remaining_ms})

    def pause(self):
        with self._lock:
            self._tick_unlocked()
            self.running = False
            self._send({"cmd": "pause"})

    def resume(self):
        with self._lock:
            if self.remaining_ms > 0:
                self.running = True
                self._ref = time.monotonic()
                self._send({"cmd": "resume"})

    def reset(self):
        with self._lock:
            self.running = False
            self.remaining_ms = 0
            self._ref = None
            self._send({"cmd": "reset"})

    def get_remaining_ms(self):
        """Return the current remaining time in ms (thread-safe snapshot)."""
        with self._lock:
            self._tick_unlocked()
            return self.remaining_ms

    def is_running(self):
        with self._lock:
            self._tick_unlocked()
            return self.running

    def _sync_loop(self):
        while not self._stop:
            time.sleep(SYNC_INTERVAL)
            with self._lock:
                self._tick_unlocked()
                if self.running:
                    self._send({"cmd": "sync", "ms": self.remaining_ms})

    def close(self):
        self._stop = True
        self.sock.close()

    # -- minigame control ---------------------------------------------------
    def start_game(self, mode):
        """Tell the matching Pico slave to start its minigame."""
        self._send({"cmd": "game", "mode": mode})
        print("[server] sent game start:", mode)

    def wait_for_result(self, timeout=70):
        """Block until a {'cmd':'result','win':bool} arrives, or timeout.

        Returns True/False on a result, or None on timeout.
        """
        self.sock.settimeout(0.5)
        deadline = time.time() + timeout
        try:
            while time.time() < deadline:
                try:
                    data, addr = self.sock.recvfrom(256)
                except socket.timeout:
                    continue
                except OSError:
                    continue
                try:
                    msg = json.loads(data)
                except (ValueError, TypeError):
                    continue
                if msg.get("cmd") == "result":
                    return bool(msg.get("win"))
            return None
        finally:
            self.sock.setblocking(True)


def main():
    """Standalone interactive test harness (not used by the game itself)."""
    server = CountdownServer()
    print("Countdown server (manual test). Commands: start <sec> | pause | resume | reset | quit")
    try:
        while True:
            line = input("> ").strip().split()
            if not line:
                continue
            cmd = line[0].lower()
            if cmd == "start" and len(line) == 2:
                server.start(float(line[1]))
            elif cmd == "pause":
                server.pause()
            elif cmd == "resume":
                server.resume()
            elif cmd == "reset":
                server.reset()
            elif cmd in ("quit", "exit"):
                break
            else:
                print("Unknown command")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        server.close()
        print("\nServer stopped.")


if __name__ == "__main__":
    main()