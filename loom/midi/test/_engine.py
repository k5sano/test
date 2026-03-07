""" Quick integration test for ot\_midi\_engine. Start the engine first: python ot\_midi\_engine.py

Then run: python test\_engine.py """

import socket import json import time

HOST = "127.0.0.1" PORT = 9100

def send\_cmd(sock: socket.socket, cmd: dict) -> dict: payload = json.dumps(cmd) + "\\n" sock.sendall(payload.encode()) buf = "" while "\\n" not in buf: buf += sock.recv(4096).decode() return json.loads(buf.strip())

def main(): sock = socket.socket(socket.AF\_INET, socket.SOCK\_STREAM) sock.connect((HOST, PORT))

```
# 1. Ping
r = send_cmd(sock, {"type": "ping"})
assert r["ok"], f"Ping failed: {r}"
print(f"[PASS] ping → {r}")

# 2. List ports
r = send_cmd(sock, {"type": "list_ports"})
assert r["ok"], f"list_ports failed: {r}"
print(f"[PASS] list_ports → {r['ports']}")

# 3. Single CC — Track Level T8 (CC46 = 80)
r = send_cmd(sock, {"type": "cc", "channel": 11, "cc": 46, "value": 80})
assert r["ok"], f"cc failed: {r}"
print(f"[PASS] cc 46=80 → {r}")

time.sleep(0.1)

# 4. Single CC — Track Level T8 (CC46 = 0, reset)
r = send_cmd(sock, {"type": "cc", "channel": 11, "cc": 46, "value": 0})
assert r["ok"], f"cc failed: {r}"
print(f"[PASS] cc 46=0 → {r}")

time.sleep(0.1)

# 5. Batch — sweep Track Level 0→127 in 8 steps
msgs = [{"channel": 11, "cc": 46, "value": v} for v in range(0, 128, 16)]
r = send_cmd(sock, {"type": "batch", "messages": msgs, "interval_ms": 20})
assert r["ok"], f"batch failed: {r}"
print(f"[PASS] batch sweep ({r['queued']} messages queued)")

time.sleep(0.5)

# 6. Bad command
r = send_cmd(sock, {"type": "unknown_thing"})
assert not r["ok"]
print(f"[PASS] bad command rejected → {r['error']}")

# 7. Value clamping (over 127)
r = send_cmd(sock, {"type": "cc", "channel": 11, "cc": 46, "value": 999})
assert r["ok"]
assert "val=127" in r["sent"]
print(f"[PASS] value clamped to 127 → {r}")

sock.close()
print("\n=== All tests passed ===")
```

if **name** == "**main**": main()