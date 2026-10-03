"""WiFi connection and non-blocking UDP command listener for the Pico 2 W.

Protocol: the Raspberry Pi broadcasts newline-terminated JSON over UDP:
    {"cmd": "start",  "ms": 60000}   -> start counting down from 60 s
    {"cmd": "pause"}                 -> pause
    {"cmd": "resume"}                -> resume
    {"cmd": "reset"}                 -> back to idle (blank)
    {"cmd": "sync",   "ms": 42350}   -> correct remaining time while running
"""
import network
import socket
import json
import time
import config


def connect_wifi():
    """Connect to the Raspberry Pi access point (blocking). Returns the WLAN object."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        deadline = time.ticks_add(time.ticks_ms(), config.WIFI_CONNECT_TIMEOUT * 1000)
        while not wlan.isconnected():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                raise RuntimeError("WiFi connection timeout")
            time.sleep_ms(200)
    print("WiFi connected:", wlan.ifconfig())
    return wlan


def scan_networks():
    """Scan for visible 2.4 GHz networks and print them. Debug helper."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("[scan] scanning...")
    try:
        nets = wlan.scan()  # list of (ssid, bssid, channel, RSSI, security, hidden)
    except Exception as e:
        print("[scan] failed:", e)
        return
    print("[scan] found {} networks:".format(len(nets)))
    for ssid, bssid, channel, rssi, security, hidden in nets:
        try:
            name = ssid.decode()
        except Exception:
            name = str(ssid)
        print("  ssid='{}' ch={} rssi={} sec={}".format(name, channel, rssi, security))


def start_wifi():
    """Begin connecting without blocking. Returns the WLAN object."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # ensure power-save mode is off (improves connection reliability on Pico W)
    try:
        wlan.config(pm=0xa11140)  # PM_NONE
    except Exception:
        pass
    print("[wifi] connecting to SSID '{}'".format(config.WIFI_SSID))
    if not wlan.isconnected():
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    return wlan


def poll_wifi(wlan):
    """Non-blocking check. Returns True once connected, False otherwise.

    Re-issues the connect() call if the link dropped (e.g. AP not up yet).
    """
    if wlan.isconnected():
        return True
    if wlan.status() < 0:
        try:
            wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        except OSError:
            pass
    return False


class UdpListener:
    """Non-blocking UDP listener that yields parsed command dicts."""

    def __init__(self, port=config.UDP_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.setblocking(False)

    def poll(self):
        """Return the most recent parsed command dict, or None if nothing waiting.

        Drains the socket so we always act on the newest packet (important for
        'sync' commands that would otherwise pile up).
        """
        latest = None
        while True:
            try:
                data, _ = self.sock.recvfrom(256)
            except OSError:
                break  # no more datagrams
            try:
                latest = json.loads(data)
            except (ValueError, TypeError):
                continue  # ignore malformed packets
        return latest