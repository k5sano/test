""" Loom MIDI CC Engine TCP server that receives JSON commands and sends MIDI CC to Octatrack via Morningstar MC8 (USB→DIN).

Usage: python ot\_midi\_engine.py \[--port 9100\] \[--midi-port 1\] """

import json import socket import threading import time import argparse import signal import sys import logging from collections import deque from dataclasses import dataclass

import rtmidi

# \---------------------------------------------------------------------------

# Logging

# \---------------------------------------------------------------------------

logging.basicConfig( level=logging.INFO, format="%(asctime)s \[%(levelname)s\] %(message)s", datefmt="%H:%M:%S", ) log = logging.getLogger("loom.midi")

# \---------------------------------------------------------------------------

# Constants

# \---------------------------------------------------------------------------

DEFAULT\_TCP\_PORT = 9100 DEFAULT\_MIDI\_PORT\_INDEX = 1 MIN\_CC\_INTERVAL\_SEC = 0.005 # 5ms rate limit OT\_AUTO\_CHANNEL = 11 # 0xBA = channel 11 status byte for CC

def cc\_status\_byte(channel: int) -> int: """MIDI CC status byte for a given channel (1-indexed).""" return 0xB0 | (channel - 1)

# \---------------------------------------------------------------------------

# Data

# \---------------------------------------------------------------------------

@dataclass class CCMessage: channel: int cc: int value: int

```
def to_bytes(self) -> list[int]:
    return [cc_status_byte(self.channel), self.cc, self.value]

def __str__(self) -> str:
    return f"CC ch={self.channel} cc={self.cc} val={self.value}"
```

# \---------------------------------------------------------------------------

# MIDI Sender (rate-limited)

# \---------------------------------------------------------------------------

class MidiSender: """ Thread-safe, rate-limited MIDI output. Messages are queued and sent from a dedicated thread. """

```
def __init__(self, port_index: int):
    self._port_index = port_index
    self._out: rtmidi.MidiOut | None = None
    self._queue: deque[CCMessage] = deque()
    self._lock = threading.Lock()
    self._event = threading.Event()
    self._running = False
    self._thread: threading.Thread | None = None
    self._last_send_time = 0.0

# -- lifecycle --

def open(self) -> bool:
    self._out = rtmidi.MidiOut()
    ports = self._out.get_ports()
    if self._port_index >= len(ports):
        log.error(
            "MIDI port index %d not found. Available: %s",
            self._port_index,
            ports or "(none)",
        )
        return False
    self._out.open_port(self._port_index)
    log.info("Opened MIDI port %d: %s", self._port_index, ports[self._port_index])
    self._running = True
    self._thread = threading.Thread(target=self._send_loop, daemon=True)
    self._thread.start()
    return True

def close(self):
    self._running = False
    self._event.set()
    if self._thread:
        self._thread.join(timeout=2.0)
    if self._out:
        self._out.close_port()
        del self._out
        self._out = None
    log.info("MIDI port closed.")

# -- public API --

def send(self, msg: CCMessage):
    with self._lock:
        self._queue.append(msg)
    self._event.set()

def send_batch(self, messages: list[CCMessage], interval_ms: int = 10):
    with self._lock:
        for msg in messages:
            self._queue.append(msg)
    self._event.set()
    # interval is enforced by the send loop (MIN_CC_INTERVAL_SEC or longer)
    # store desired interval for this batch
    self._batch_interval = max(interval_ms / 1000.0, MIN_CC_INTERVAL_SEC)

def list_ports(self) -> list[str]:
    probe = rtmidi.MidiOut()
    ports = probe.get_ports()
    del probe
    return ports

# -- internal --

def _send_loop(self):
    while self._running:
        self._event.wait(timeout=0.1)
        self._event.clear()
        while self._queue and self._running:
            with self._lock:
                if not self._queue:
                    break
                msg = self._queue.popleft()

            # rate limit
            elapsed = time.monotonic() - self._last_send_time
            wait = MIN_CC_INTERVAL_SEC - elapsed
            if wait > 0:
                time.sleep(wait)

            if self._out:
                self._out.send_message(msg.to_bytes())
                self._last_send_time = time.monotonic()
                log.info("SENT %s", msg)
            else:
                log.warning("MIDI port not open, dropped: %s", msg)
```

# \---------------------------------------------------------------------------

# TCP Server

# \---------------------------------------------------------------------------

class TCPServer: """ Single-threaded TCP server (one client at a time). Accepts newline-delimited JSON commands. """

```
def __init__(self, midi: MidiSender, host: str = "127.0.0.1", port: int = DEFAULT_TCP_PORT):
    self._midi = midi
    self._host = host
    self._port = port
    self._sock: socket.socket | None = None
    self._running = False

def start(self):
    self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._sock.settimeout(1.0)
    self._sock.bind((self._host, self._port))
    self._sock.listen(4)
    self._running = True
    log.info("TCP listening on %s:%d", self._host, self._port)

    while self._running:
        try:
            conn, addr = self._sock.accept()
        except socket.timeout:
            continue
        except OSError:
            break
        log.info("Client connected: %s", addr)
        self._handle_client(conn)

def stop(self):
    self._running = False
    if self._sock:
        self._sock.close()
    log.info("TCP server stopped.")

# -- internal --

def _handle_client(self, conn: socket.socket):
    buf = ""
    conn.settimeout(0.5)
    try:
        while self._running:
            try:
                data = conn.recv(4096)
            except socket.timeout:
                continue
            if not data:
                break
            buf += data.decode("utf-8", errors="replace")

            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                response = self._dispatch(line)
                conn.sendall((json.dumps(response) + "\n").encode())
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        conn.close()
        log.info("Client disconnected.")

def _dispatch(self, raw: str) -> dict:
    try:
        cmd = json.loads(raw)
    except json.JSONDecodeError as e:
        log.warning("Bad JSON: %s", e)
        return {"ok": False, "error": f"Invalid JSON: {e}"}

    msg_type = cmd.get("type", "")
    log.info("RECV %s", cmd)

    if msg_type == "cc":
        return self._handle_cc(cmd)
    elif msg_type == "batch":
        return self._handle_batch(cmd)
    elif msg_type == "list_ports":
        return self._handle_list_ports()
    elif msg_type == "ping":
        return {"ok": True, "pong": True}
    else:
        return {"ok": False, "error": f"Unknown type: {msg_type}"}

def _handle_cc(self, cmd: dict) -> dict:
    try:
        msg = CCMessage(
            channel=cmd.get("channel", OT_AUTO_CHANNEL),
            cc=int(cmd["cc"]),
            value=max(0, min(127, int(cmd["value"]))),
        )
    except (KeyError, ValueError) as e:
        return {"ok": False, "error": f"Bad cc command: {e}"}

    self._midi.send(msg)
    return {"ok": True, "sent": str(msg)}

def _handle_batch(self, cmd: dict) -> dict:
    raw_messages = cmd.get("messages", [])
    if not raw_messages:
        return {"ok": False, "error": "Empty batch"}

    messages = []
    for m in raw_messages:
        try:
            messages.append(CCMessage(
                channel=m.get("channel", OT_AUTO_CHANNEL),
                cc=int(m["cc"]),
                value=max(0, min(127, int(m["value"]))),
            ))
        except (KeyError, ValueError) as e:
            return {"ok": False, "error": f"Bad message in batch: {e}"}

    interval_ms = cmd.get("interval_ms", 10)
    self._midi.send_batch(messages, interval_ms)
    return {"ok": True, "queued": len(messages)}

def _handle_list_ports(self) -> dict:
    ports = self._midi.list_ports()
    return {"ok": True, "ports": ports}
```

# \---------------------------------------------------------------------------

# Main

# \---------------------------------------------------------------------------

def main(): parser = argparse.ArgumentParser(description="Loom MIDI CC Engine") parser.add\_argument("--port", type=int, default=DEFAULT\_TCP\_PORT, help="TCP port (default: 9100)") parser.add\_argument("--midi-port", type=int, default=DEFAULT\_MIDI\_PORT\_INDEX, help="MIDI port index (default: 1)") args = parser.parse\_args()

```
midi = MidiSender(args.midi_port)
if not midi.open():
    log.error("Failed to open MIDI port. Exiting.")
    sys.exit(1)

server = TCPServer(midi, port=args.port)

def shutdown(sig, frame):
    log.info("Shutting down (signal %s)...", sig)
    server.stop()
    midi.close()
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

try:
    server.start()
finally:
    midi.close()
```

if **name** == "**main**": main()